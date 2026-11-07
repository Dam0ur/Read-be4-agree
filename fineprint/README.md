# FinePrint
*Don't just agree. Understand.*

FinePrint turns terms and conditions into plain English. Paste any terms, and an AI finds the clauses that matter (data sharing, auto-renewal, fees, giving up legal rights, content ownership), rates each one low, medium or high risk, and gives an overall verdict: safe, caution or avoid.

**Demo video:** [paste your YouTube link here]

## The problem
Most people click "I agree" without reading. Terms and conditions are written by lawyers and hide clauses that share your data, renew your subscription, or take away your right to sue.

## How it works
1. You paste terms into the page (or click "Try a sample").
2. The Python backend (`app.py`, built with Flask) sends them to Google's Gemini model with a prompt that asks for a strict JSON answer.
3. The backend checks the answer, drops anything invalid, and sorts clauses from high to low risk.
4. The page shows a verdict badge and colour-coded cards, each with a plain-English explanation and the original wording.

The API key is only read on the server (environment variable `GEMINI_API_KEY`). It is never sent to the browser or stored in this repo.

## Run it
```
pip install -r requirements.txt
export GEMINI_API_KEY="your-key"        # Windows PowerShell: $env:GEMINI_API_KEY="your-key"
python app.py
```
Open http://127.0.0.1:5000

`Main.py` is the original command-line version: `python Main.py terms.txt`.

## Files
- `app.py`: backend (Flask) and Gemini call
- `templates/index.html`: the single-page interface
- `Main.py`: command-line version
- `requirements.txt`: dependencies

## Tools used
Python, Flask, Google Gemini API (`gemini-2.5-flash`), plain HTML/CSS/JavaScript.

## What's next
More languages (starting with French), and a browser extension that warns you before you click "I agree".

## Team
[your names]
