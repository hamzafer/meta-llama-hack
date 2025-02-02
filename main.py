#!/usr/bin/env python3
"""
Google Search API + Llama3.3 (Ollama) for Translation & Summarization.
- Uses Google Search API (with location-based search)
- Uses Llama3.3 (Ollama) for translations (query/result)
- Summarizes results with Llama3.3
"""

import os
import requests
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "http://localhost:11434/api/generate")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.3:70b")
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "no")

app = Flask(__name__)


def call_llama(prompt: str) -> str:
    """
    Calls the Llama model via a local API.
    """
    payload = {
        "model": LLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(LLAMA_API_URL, json=payload)
        response.raise_for_status()
        result_json = response.json()
        return result_json.get("response", "Error: No response from Llama")
    except requests.RequestException as e:
        return f"Error calling Llama: {e}"


def llama_translate(text: str, target_lang: str) -> str:
    """
    Uses Llama to translate text into the target language.
    """
    prompt = f"Translate the following text into {target_lang}. ONLY output the translated text:\n\n{text}\n\nTranslation:"
    return call_llama(prompt)


def google_search(query, gl=DEFAULT_COUNTRY, hl=DEFAULT_LANG):
    """
    Calls Google Custom Search API with location and language-based filtering.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "gl": gl,
        "hl": hl
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        if "error" in results:
            print("Google API Error:", results["error"])
            return []
        return results.get("items", [])
    except requests.RequestException as e:
        print("Google API Exception:", e)
        return []


def get_webpage_text(url: str) -> str:
    """
    Fetches webpage content and extracts text.
    """
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator="\n")[:1000]
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


@app.route("/", methods=["GET", "POST"])
def index():
    results, summary = [], ""
    if request.method == "POST":
        query = request.form.get("query")
        comm_lang = request.form.get("comm_lang", DEFAULT_LANG)
        if query:
            translated_query = llama_translate(query, "Norwegian")
            search_results = google_search(translated_query)
            articles = {result.get("title"): result.get("snippet") for result in search_results if
                        result.get("title") and result.get("snippet")}
            prompt = "\n".join(
                [f"{i}. {title}: {snippet}" for i, (title, snippet) in enumerate(articles.items(), start=1)])
            translated_text = llama_translate(prompt, comm_lang)
            summary_prompt = f"Summarize the following in English:\n\n{translated_text}\n\nSummary:"
            summary = call_llama(summary_prompt)
            results = search_results
    return render_template("index.html", results=results, summary=summary)


if __name__ == "__main__":
    app.run(debug=True)
