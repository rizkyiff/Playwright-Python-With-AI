# Import modul json untuk serialisasi request body dan parsing response
import json
# Import modul logging untuk pencatatan log
import logging
# Import modul os untuk membaca environment variable (AI_API_KEY, AI_BASE_URL, AI_MODEL)
import os
# Import urllib.request untuk HTTP request ke AI API
import urllib.request

# Buat logger untuk modul ini
logger = logging.getLogger(__name__)


# Function: menganalisis traceback test failure dan memberikan diagnostic + rekomendasi
def triage_failure(exception_info: str) -> str:
    """
    Analyzes test failure stack trace using AI Model if AI_API_KEY is configured,
    or falls back to smart diagnostic heuristics. Logs analysis to console.
    """
    ai_api_key = os.getenv("AI_API_KEY")  # Baca API key dari environment variable
    # Susun prompt untuk AI — minta analisis root cause 2-bullet dalam bahasa Indonesia
    # Truncate traceback ke 1500 karakter terakhir untuk efisiensi token
    prompt = (
        "Analyze this automated Playwright test failure traceback and provide a concise, "
        "actionable 2-bullet point root cause diagnostic and fix recommendation in Indonesian:\n\n"
        f"Traceback:\n{exception_info[-1500:]}"  # Ambil 1500 char terakhir (bagian paling relevan)
    )

    # Print header diagnostic ke console
    print("\n=================== [AI FAILURE TRIAGE DIAGNOSTIC] ===================")
    print("[AI Failure Triage] Analyzing test failure traceback...")

    # === MODE AI (jika API key tersedia) ===
    if ai_api_key:
        print("[AI Failure Triage] AI_API_KEY detected. Invoking AI Triage Model...")
        try:
            # Baca konfigurasi AI dari environment variable
            base_url = os.getenv("AI_BASE_URL", "https://ai.sumopod.com/v1").rstrip("/")  # Base URL API
            ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")  # Model AI
            url = f"{base_url}/chat/completions"  # Endpoint chat completions
            # Header HTTP: content-type + authorization
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ai_api_key}",
            }
            # Body request: system prompt (peran AI) + user prompt (traceback)
            payload = {
                "model": ai_model,
                "messages": [
                    {
                        "role": "system",  # System message: set persona AI sebagai QA expert
                        "content": "You are an expert QA Automation Engineer specialized in Playwright Python and Pytest.",
                    },
                    {"role": "user", "content": prompt},  # User message: traceback + instruksi
                ],
                "temperature": 0.2,  # Temperature rendah (0.2) = output presisi, deterministik
            }
            # Buat dan kirim HTTP POST request
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:  # Timeout 10 detik
                res_body = response.read().decode("utf-8")  # Baca response body
                res_json = json.loads(res_body)  # Parse JSON
                diagnosis = res_json["choices"][0]["message"]["content"].strip()  # Ambil output AI
                # Print hasil analisis AI ke console
                print(f"\n[AI Failure Triage Output]:\n{diagnosis}")
                print("=======================================================================\n")
                return diagnosis  # Return diagnosis dari AI
        except Exception as e:
            # Jika AI API error (timeout, parsing error, dll) → log error, lanjut ke fallback
            print(f"[AI Failure Triage] Error invoking AI API ({e}). Falling back to heuristic triage.")

    # === MODE HEURISTIC FALLBACK (tanpa AI) ===
    # Analisis traceback menggunakan pattern matching sederhana
    print("[AI Failure Triage] Applying diagnostic triage rules:")
    if "KeyError" in exception_info:
        # Pattern: KeyError — biasanya typo pada nama key dictionary
        diagnosis = (
            "[ROOT CAUSE]: KeyError encountered when accessing dictionary key.\n"
            "[RECOMMENDED FIX]: Verify variable/dictionary key spelling (e.g. check for typos like 'company_namea')."
        )
    elif "TimeoutError" in exception_info:
        # Pattern: TimeoutError — elemen tidak ditemukan dalam waktu yang ditentukan
        diagnosis = (
            "[ROOT CAUSE]: Locator wait timeout exceeded.\n"
            "[RECOMMENDED FIX]: Verify element visibility in DOM or check if locator XPath requires contains(text(), ...)."
        )
    elif "AssertionError" in exception_info:
        # Pattern: AssertionError — ekspektasi test tidak sesuai dengan realita
        diagnosis = (
            "[ROOT CAUSE]: Assertion condition failed.\n"
            "[RECOMMENDED FIX]: Inspect expected data vs actual DOM element content."
        )
    else:
        # Pattern lainnya — ambil baris terakhir traceback sebagai clue
        last_line = exception_info.splitlines()[-1] if exception_info.splitlines() else exception_info
        diagnosis = f"[ROOT CAUSE]: Test execution exception.\n[RECOMMENDED FIX]: Inspect error log: {last_line}"

    # Print hasil heuristic ke console
    print(diagnosis)
    print("=======================================================================\n")
    return diagnosis  # Return diagnosis heuristic
