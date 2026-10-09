# 🌱 StreetSignal

Local AI for community issue reporting. Upload a photo of a public infrastructure
problem — a pothole, garbage, a broken streetlight, waterlogging — and let a
**locally-run** AI vision model draft an editable civic report. Nothing is
submitted anywhere without your review and consent.

## Features

- 📸 Upload (or capture) a photo of a civic issue
- 🤖 Image analysis through a **local Ollama** vision model (`qwen2.5vl:3b`) — no paid AI APIs
- 📝 Editable report: issue category, visible observations, suggested severity, uncertainty
- ⚠️ Every report is clearly labeled as AI-assisted and not submitted to any authority

## In progress

- SQLite persistence with report history, search and filters
- State / city / locality capture across India's 28 states and 8 union territories
- Configurable authority directory (no invented contact information)
- PDF / TXT report exports
- Privacy protection and citizen review before any submission

## Stack

| Layer | Technology |
|---|---|
| UI | Python + Streamlit |
| AI | Local Ollama API, vision model `qwen2.5vl:3b` |
| Storage | SQLite (planned) |

## Run it

Requires [Ollama](https://ollama.com) installed locally, with the vision model pulled:

```bash
ollama pull qwen2.5vl:3b
```

Then, from this folder:

```powershell
python -m venv .venv312
.venv312\Scripts\python.exe -m pip install -r requirements.txt
.venv312\Scripts\python.exe -m streamlit run app.py
```

The app opens at http://localhost:8501.

## Privacy & honesty

- Photos are analyzed **on your own machine** through your local Ollama instance.
- AI observations may be inaccurate — every field is editable and requires human review.
- Reports are never submitted to any authority automatically. A report is only
  ever handed to you (as JSON) for your own review, and exported files state
  plainly that no authority has received anything.
