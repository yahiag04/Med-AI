# MedAI

MedAI is a FastAPI web application that lets clinicians upload chest X-rays, associate them with patient records, and receive a pneumonia prediction with urgency ordering.

This project is an academic prototype focused on machine learning experimentation and user-friendly visualization. It is **not** a medical device and must not be used for diagnostic or clinical decisions.

---

## Features

- Authentication (session-based)
- Patient record creation
- X-ray upload + pneumonia prediction
- Urgency sorting (pneumonia cases prioritized)
- Lightweight, modern UI with Bootstrap
- PostgreSQL storage

---

## Tech Stack

- Python
- FastAPI
- PostgreSQL
- PyTorch
- Bootstrap

---

## Installation

```bash
pip install -r requirements.txt
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/medai"
uvicorn app:app --reload
```

Set a secret for session cookies before running in production:

```bash
export APP_SECRET_KEY="your-strong-secret"
```

---

## Docker

```bash
docker compose up --build
```

If you have legacy SQLite data in `app.db`, migrate it with:

```bash
python scripts/migrate_sqlite_to_postgres.py --sqlite-path app.db --truncate
```

---

## Future Development

MedAI will expand beyond pneumonia to support additional disease detection models and multi-model selection within the same clinical workflow.

---

## Disclaimer

This tool is for **research and educational purposes only**. It is not approved for medical use and must not replace professional interpretation.
