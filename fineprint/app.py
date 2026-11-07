"""FinePrint - web app that explains terms and conditions in plain English.

Run:
    pip install -r requirements.txt
    export GEMINI_API_KEY="your-key"      (Windows PowerShell: $env:GEMINI_API_KEY="your-key")
    python app.py
Then open http://127.0.0.1:5000

The API key is only read on the server. It is never sent to the browser.
"""
import json
import os

from flask import Flask, jsonify, render_template, request

MODEL = "gemini-2.5-flash"  # if "model not found", copy the current name from AI Studio > Get code
MAX_CHARS = 30000

PROMPT = """You are a consumer-rights expert explaining to a teenager.
Find the clauses in these terms that matter to the user: data sharing, auto-renewal, fees, giving up legal rights, content ownership.
Return JSON only, in exactly this shape:
{"verdict": "safe" or "caution" or "avoid",
 "verdict_reason": "one sentence",
 "clauses": [{"quote": "short original wording", "risk": "low" or "medium" or "high", "explanation": "one plain-English sentence"}]}

TERMS:
"""

app = Flask(__name__)
_client = None


def get_client():
    """Create the Gemini client once, on first use."""
    global _client
    if _client is None:
        from google import genai
        from google.genai import types

        _client = genai.Client(
            api_key=os.environ["GEMINI_API_KEY"],
            http_options=types.HttpOptions(
                api_version="v1beta",
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
    return _client


def call_gemini(text):
    """Send the terms to Gemini and return the raw JSON text it answers with."""
    response = get_client().models.generate_content(
        model=MODEL,
        contents=PROMPT + text,
        config={"response_mime_type": "application/json"},
    )
    return response.text


def clean_result(raw):
    """Parse and validate the AI answer. Raises ValueError if it is unusable."""
    raw = (raw or "").strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("answer is not an object")

    verdict = str(data.get("verdict", "")).lower()
    if verdict not in ("safe", "caution", "avoid"):
        raise ValueError("bad verdict")

    clauses = []
    for c in data.get("clauses", []):
        risk = str(c.get("risk", "")).lower()
        if risk not in ("low", "medium", "high"):
            continue
        clauses.append(
            {
                "risk": risk,
                "explanation": str(c.get("explanation", "")).strip(),
                "quote": str(c.get("quote", "")).strip(),
            }
        )
    order = {"high": 0, "medium": 1, "low": 2}
    clauses.sort(key=lambda c: order[c["risk"]])

    return {
        "verdict": verdict,
        "verdict_reason": str(data.get("verdict_reason", "")).strip(),
        "clauses": clauses,
    }


@app.get("/")
def index():
    return render_template("index.html", max_chars=MAX_CHARS)


@app.post("/api/analyze")
def analyze():
    body = request.get_json(silent=True) or {}
    text = body.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify(error="Paste some terms first."), 400
    if len(text) > MAX_CHARS:
        return jsonify(error=f"That's too long. The limit is {MAX_CHARS:,} characters."), 413

    try:
        return jsonify(clean_result(call_gemini(text)))
    except Exception as e:  # keep the real error in the server log, show a friendly one
        app.logger.error("Analysis failed: %r", e)
        return jsonify(error="Something went wrong. Try again."), 502


if __name__ == "__main__":
    if "GEMINI_API_KEY" not in os.environ:
        print("Set GEMINI_API_KEY first, for example:  export GEMINI_API_KEY=\"your-key\"")
    app.run(debug=False, port=5000)
