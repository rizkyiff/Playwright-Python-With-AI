import json
import logging
import os
import urllib.request

logger = logging.getLogger(__name__)


def triage_failure(exception_info: str) -> str:
    """
    Analyzes test failure stack trace using AI Model if AI_API_KEY is configured,
    or falls back to smart diagnostic heuristics. Logs analysis to console.
    """
    ai_api_key = os.getenv("AI_API_KEY")
    prompt = (
        "Analyze this automated Playwright test failure traceback and provide a concise, "
        "actionable 2-bullet point root cause diagnostic and fix recommendation in Indonesian:\n\n"
        f"Traceback:\n{exception_info[-1500:]}"
    )

    print("\n=================== [AI FAILURE TRIAGE DIAGNOSTIC] ===================")
    print("[AI Failure Triage] Analyzing test failure traceback...")

    if ai_api_key:
        print("[AI Failure Triage] AI_API_KEY detected. Invoking AI Triage Model...")
        try:
            base_url = os.getenv("AI_BASE_URL", "https://ai.sumopod.com/v1").rstrip("/")
            ai_model = os.getenv("AI_MODEL", "gpt-4o-mini")
            url = f"{base_url}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {ai_api_key}",
            }
            payload = {
                "model": ai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert QA Automation Engineer specialized in Playwright Python and Pytest.",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            }
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                diagnosis = res_json["choices"][0]["message"]["content"].strip()
                print(f"\n[AI Failure Triage Output]:\n{diagnosis}")
                print("=======================================================================\n")
                return diagnosis
        except Exception as e:
            print(f"[AI Failure Triage] Error invoking AI API ({e}). Falling back to heuristic triage.")

    # Heuristic Triage Fallback
    print("[AI Failure Triage] Applying diagnostic triage rules:")
    if "KeyError" in exception_info:
        diagnosis = (
            "[ROOT CAUSE]: KeyError encountered when accessing dictionary key.\n"
            "[RECOMMENDED FIX]: Verify variable/dictionary key spelling (e.g. check for typos like 'company_namea')."
        )
    elif "TimeoutError" in exception_info:
        diagnosis = (
            "[ROOT CAUSE]: Locator wait timeout exceeded.\n"
            "[RECOMMENDED FIX]: Verify element visibility in DOM or check if locator XPath requires contains(text(), ...)."
        )
    elif "AssertionError" in exception_info:
        diagnosis = (
            "[ROOT CAUSE]: Assertion condition failed.\n"
            "[RECOMMENDED FIX]: Inspect expected data vs actual DOM element content."
        )
    else:
        last_line = exception_info.splitlines()[-1] if exception_info.splitlines() else exception_info
        diagnosis = f"[ROOT CAUSE]: Test execution exception.\n[RECOMMENDED FIX]: Inspect error log: {last_line}"

    print(diagnosis)
    print("=======================================================================\n")
    return diagnosis
