# AI Usage & Data Generation Guide

Dokumen ini menjelaskan integrasi dan penggunaan AI pada framework otomatisasi ini.

## Principles of AI Usage
1. **Realistic Indonesian Data Generation**: AI digunakan untuk menyusun profil perusahaan Indonesia yang realistis.
2. **Schema Validation**: Setiap data bentukan AI / generator wajib tervalidasi menggunakan Pydantic model (`ai/schemas.py`).
3. **Deterministic Fallback**: Jika `AI_API_KEY` tidak tersedia atau API error, generator secara otomatis menggunakan fallback deterministic berbasis library `Faker`.
4. **No Assertion Relaxation**: AI tidak pernah digunakan untuk melonggarkan assertion, mengabaikan error, atau mengubah ekspektasi validasi bisnis.

## Attachments to Allure
Data perusahaan yang dihasilkan dan digunakan dalam test akan selalu di-attach secara transparan ke dalam Allure Report (`Company test data used`).
