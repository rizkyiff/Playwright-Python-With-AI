# AI Usage & Data Generation Guide

Dokumen ini menjelaskan integrasi dan penggunaan AI pada framework otomatisasi ini.

---

## Principles of AI Usage

1. **Realistic Indonesian Data Generation**: AI digunakan untuk menyusun profil perusahaan Indonesia yang realistis (nama, alamat, wilayah administratif yang valid).
2. **Schema Validation**: Setiap data bentukan AI / generator wajib tervalidasi menggunakan Pydantic model (`ai/schemas.py` → `CompanyData`).
3. **Deterministic Fallback**: Jika `AI_API_KEY` tidak tersedia atau API error, generator secara otomatis menggunakan fallback deterministic berbasis library `Faker` tanpa menghentikan eksekusi test.
4. **No Assertion Relaxation**: AI tidak pernah digunakan untuk melonggarkan assertion, mengabaikan error, atau mengubah ekspektasi validasi bisnis.

---

## AI Modules Overview

### 1. AI Data Generation (`ai/generated_data.py`)

Modul ini memanggil AI model API untuk menghasilkan data perusahaan Indonesia yang realistis berdasarkan prompt terstruktur.

**Alur kerja:**
```
get_company_data() → [AI_API_KEY exists?]
    ├── YES → generate_ai_company_data() → AI API call → Pydantic validation → return data
    │         (on error) → fallback to Faker
    └── NO  → generate_deterministic_company_data() → Faker + Pydantic validation → return data
```

**Konfigurasi environment:**
| Variable | Default | Keterangan |
|----------|---------|------------|
| `AI_API_KEY` | _(kosong)_ | API key untuk AI model. Jika kosong, fallback ke Faker |
| `AI_BASE_URL` | `https://ai.sumopod.com/v1` | Base URL endpoint API (OpenAI-compatible) |
| `AI_MODEL` | `gpt-4o-mini` | Model yang digunakan untuk generasi data |

**Prompt strategy:**
- Temperature: `0.7` (cukup kreatif untuk variasi data, tetap terkontrol)
- Response format: `json_object` (memaksa output JSON valid)
- Constraints di-embed dalam prompt (max 30 char nama, format telepon `08xxx`, wilayah UPPERCASE)

### 2. AI Failure Triage (`ai/failure_triage.py`)

Modul ini menganalisis stack trace test failure secara otomatis dan memberikan diagnostic + rekomendasi fix.

**Alur kerja:**
```
Test FAILED → pytest hook (conftest.py) → triage_failure(traceback)
    ├── AI_API_KEY exists → AI analysis (2-bullet root cause & fix)
    └── No API key       → Heuristic rules (KeyError, TimeoutError, AssertionError patterns)
```

**Prompt strategy:**
- Temperature: `0.2` (rendah untuk diagnostic yang presisi)
- Traceback di-truncate ke 1500 karakter terakhir untuk efisiensi token
- System prompt: "Expert QA Automation Engineer specialized in Playwright Python and Pytest"

**Output di-attach ke Allure report** sebagai `AI Failure Triage Analysis` (text attachment).

---

## Contoh Output

### AI Mode (dengan API key):
```
[AI Data Factory] AI_API_KEY detected. Invoking AI Data Generator...
[AI Generator] Requesting AI Model for test data generation...
[AI Generator] Schema Validation SUCCESS!

=================== [COMPANY TEST DATA USED] ===================
  company_name  : PT QA Maju Sejahtera 8721
  email         : qa.test@majusejahtera.co.id
  phone         : 081234567890
  province      : DKI JAKARTA
  city          : JAKARTA SELATAN
  ...
=================================================================
```

### Faker Fallback Mode (tanpa API key):
```
[AI Data Factory] AI_API_KEY not configured. Falling back to deterministic Faker data generator.

=================== [COMPANY TEST DATA USED] ===================
  company_name  : PT QA Dewi 4523
  email         : qa.4523.dewi@gmail.com
  phone         : 08512345678
  province      : DKI JAKARTA
  city          : JAKARTA UTARA
  ...
=================================================================
```

---

## Attachments to Allure

- **Company test data**: Data perusahaan yang dihasilkan dan digunakan dalam test akan selalu di-attach ke Allure Report (`Company test data used`).
- **Failure triage**: Jika test gagal, hasil analisis AI/heuristic di-attach sebagai `AI Failure Triage Analysis`.
- **Failure screenshot**: Screenshot full-page otomatis di-attach saat test gagal.

---

## Cara Mengaktifkan / Menonaktifkan AI Mode

```powershell
# Aktifkan AI mode — set API key di .env
AI_API_KEY=your-api-key-here

# Nonaktifkan AI mode — kosongkan atau hapus API key
AI_API_KEY=
```

Tidak perlu mengubah kode apapun. Modul secara otomatis mendeteksi ketersediaan `AI_API_KEY` dan memilih generator yang sesuai.
