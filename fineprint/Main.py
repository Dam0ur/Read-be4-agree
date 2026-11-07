 
import os
import sys
import json
from google import genai
from google.genai import types

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(
        api_version="v1beta",
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)

MODEL = "gemini-2.5-flash" 
PROMPT = """You are a consumer-rights expert explaining to a teenager.
Find the clauses in these terms that matter to the user: data sharing, auto-renewal, fees, giving up legal rights, content ownership.
Return JSON in exactly this shape:
{"verdict": "safe" or "caution" or "avoid",
 "verdict_reason": "one sentence",
 "clauses": [{"quote": "short original wording", "risk": "low" or "medium" or "high", "explanation": "one plain-English sentence"}]}

TERMS:
"""

def analyze(text):
    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT + text[:30000],
        config={"response_mime_type": "application/json"},
    )
    print("Gemini API response:")
    print(response.text)
    return json.loads(response.text)

def main():
    if len(sys.argv) >= 2:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        print("Paste the terms below. Enter END on its own line to analyze:")
        lines = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            if line.strip() == "END":
                break
            lines.append(line)
        text = "\n".join(lines)
    if not text.strip():
        print("No terms provided. Pass a text file or paste terms into the terminal.")
        return
    try:
        result = analyze(text)
    except Exception as e:
        print("Error:", e)
        return

    labels = {"high": "[HIGH]  ", "medium": "[MEDIUM]", "low": "[LOW]   "}
    order = {"high": 0, "medium": 1, "low": 2}
    print(f"\nVERDICT: {result['verdict'].upper()} - {result['verdict_reason']}\n")
    for c in sorted(result["clauses"], key=lambda c: order.get(c["risk"], 3)):
        print(f"{labels.get(c['risk'], '[?]')} {c['explanation']}")
        print(f'         "{c["quote"]}"\n')

if __name__ == "__main__":
    main()