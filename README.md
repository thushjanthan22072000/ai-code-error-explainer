# DebugMate — AI Code Error Explainer

A Flask web app to run code in multiple languages and explain errors with Google's Gemini API.

## Included languages
Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, PHP, Ruby, Kotlin, Swift, R, Perl, Bash, Lua, and Dart.

## Requirements
- Python 3.10+
- Gemini API key for AI explanations
- Internet access for the external Piston execution service and Gemini

## Setup (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and add your Gemini key:
```env
GEMINI_API_KEY=your_actual_key
```
Start:
```powershell
python app.py
```
Open http://127.0.0.1:5050/

## How it works
- **Run Code** sends the selected language, code and optional standard input to the Piston API.
- **Explain Error** sends the code and error text to Gemini.
- Submitted code is executed by an external code execution service, not directly by this Flask app.

## Important safety and availability notes
- Do not submit passwords, API keys, personal data, or confidential code.
- The execution service is external and may have rate limits, temporary downtime, or language-version changes.
- Execution is limited by request timeouts, but do not rely on a public execution API for sensitive or production workloads.
- For a public deployment, use a properly isolated, maintained sandbox service with strict CPU, memory, network, and time limits. Never execute arbitrary user code directly on your Flask server.
- Gemini API key stays in your server-side `.env` file. Never commit `.env` to GitHub.
