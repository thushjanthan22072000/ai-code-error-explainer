
import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)

# Gemini AI configuration
API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

# Local Piston Docker service
PISTON_URL = "http://127.0.0.1:2000/api/v2"

# All 17 installed programming languages
LANGUAGES = {
    "Python": {
        "language": "python",
        "version": "3.12.0",
        "filename": "main.py"
    },
    "JavaScript": {
        "language": "javascript",
        "version": "18.15.0",
        "filename": "main.js"
    },
    "TypeScript": {
        "language": "typescript",
        "version": "5.0.3",
        "filename": "main.ts"
    },
    "Java": {
        "language": "java",
        "version": "15.0.2",
        "filename": "Main.java"
    },
    "C": {
        "language": "c",
        "version": "10.2.0",
        "filename": "main.c"
    },
    "C++": {
        "language": "c++",
        "version": "10.2.0",
        "filename": "main.cpp"
    },
    "C#": {
        "language": "csharp.net",
        "version": "5.0.201",
        "filename": "Main.cs"
    },
    "Go": {
        "language": "go",
        "version": "1.16.2",
        "filename": "main.go"
    },
    "Rust": {
        "language": "rust",
        "version": "1.68.2",
        "filename": "main.rs"
    },
    "PHP": {
        "language": "php",
        "version": "8.2.3",
        "filename": "main.php"
    },
    "Ruby": {
        "language": "ruby",
        "version": "3.0.1",
        "filename": "main.rb"
    },
    "Kotlin": {
        "language": "kotlin",
        "version": "1.8.20",
        "filename": "Main.kt"
    },
    "Swift": {
        "language": "swift",
        "version": "5.3.3",
        "filename": "main.swift"
    },
    "R": {
        "language": "rscript",
        "version": "4.1.1",
        "filename": "main.r"
    },
    "Perl": {
        "language": "perl",
        "version": "5.36.0",
        "filename": "main.pl"
    },
    "Bash": {
        "language": "bash",
        "version": "5.2.0",
        "filename": "main.sh"
    },
    "Lua": {
        "language": "lua",
        "version": "5.4.4",
        "filename": "main.lua"
    }
}


@app.get("/")
def home():
    return render_template(
        "index.html",
        languages=list(LANGUAGES.keys())
    )


@app.post("/run")
def run_code():

    data = request.get_json(silent=True) or {}

    language_name = data.get("language", "")
    code = (data.get("code") or "").strip()
    stdin = data.get("stdin") or ""

    # Input validation
    if language_name not in LANGUAGES:
        return jsonify({
            "error": "Please select a supported programming language."
        }), 400

    if not code:
        return jsonify({
            "error": "Please enter code before running it."
        }), 400

    if len(code) > 20000:
        return jsonify({
            "error": "Code is too long. Maximum 20,000 characters."
        }), 400

    if len(stdin) > 5000:
        return jsonify({
            "error": "Input is too long. Maximum 5,000 characters."
        }), 400

    config = LANGUAGES[language_name]

    # Piston execution request
    payload = {
        "language": config["language"],
        "version": config["version"],
        "files": [
            {
                "name": config["filename"],
                "content": code
            }
        ],
        "stdin": stdin,
        "run_timeout": 3000,
        "compile_timeout": 3000
    }

    try:

        response = requests.post(
            f"{PISTON_URL}/execute",
            json=payload,
            timeout=30
        )

        # Show actual Piston errors
        if not response.ok:

            print("PISTON STATUS:", response.status_code)
            print("PISTON ERROR:", response.text)

            try:
                details = response.json()
            except ValueError:
                details = response.text

            return jsonify({
                "error": "Piston execution error",
                "details": details
            }), response.status_code

        result = response.json()

        compile_result = result.get("compile") or {}
        run_result = result.get("run") or {}

        output = run_result.get("output", "")

        if compile_result.get("output"):
            output = compile_result["output"] + (
                "\n" + output if output else ""
            )

        return jsonify({
            "output": output or "(No output)",
            "stderr": run_result.get("stderr", ""),
            "exitCode": run_result.get("code"),
            "signal": run_result.get("signal"),
            "language": language_name,
            "ran": True
        })

    except requests.Timeout:

        return jsonify({
            "error": "Execution request timed out. Please try again."
        }), 504

    except requests.RequestException:

        app.logger.exception("Piston connection failed")

        return jsonify({
            "error": "Cannot connect to Piston. Check Docker Desktop."
        }), 502

    except (ValueError, KeyError):

        return jsonify({
            "error": "Unexpected response from Piston."
        }), 502


@app.post("/analyze")
def analyze():

    data = request.get_json(silent=True) or {}

    language = (data.get("language") or "Python").strip()
    code = (data.get("code") or "").strip()
    error = (data.get("error") or "").strip()

    if not code or not error:
        return jsonify({
            "error": "Please enter both code and error message."
        }), 400

    if client is None:
        return jsonify({
            "error": "Gemini API key is missing. Check your .env file."
        }), 503

    prompt = f"""
You are a patient programming tutor.

Explain this {language} programming error for a beginner.

Use these headings:

1. What the error means
2. Why it happened
3. How to fix it
4. Corrected code
5. How to avoid it next time

Use simple English and practical examples.
Include corrected code in a fenced code block.

Do not claim code was tested unless it was actually executed.

CODE:
{code}

ERROR:
{error}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return jsonify({
            "explanation": response.text or "No explanation returned."
        })

    except Exception:

        app.logger.exception("Gemini analysis failed")

        return jsonify({
            "error": "Could not analyze the error. Check your Gemini API key."
        }), 502


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5050,
        debug=True
    )
