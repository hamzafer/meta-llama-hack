#!/usr/bin/env python3
"""
Google Search API + Llama3.3 (Ollama) for Translation & Summarization.
- Uses Google Search API (with location-based search)
- Uses Llama3.3 (Ollama) for translations (query/result)
- Summarizes results with Llama3.3
"""

import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, request, render_template

# Load environment variables from a .env file if present
load_dotenv()

# Core configuration (can be overridden via environment variables)
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "http://localhost:11435/api/generate")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.3")
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "no")

# Additional configurable parameters to eliminate hardcoded values:
GOOGLE_SEARCH_API_URL = os.getenv("GOOGLE_SEARCH_API_URL", "https://www.googleapis.com/customsearch/v1")
# QUERY_TRANSLATION_LANG = os.getenv("QUERY_TRANSLATION_LANG", "Norwegian")
QUERY_TRANSLATION_LANG = os.getenv("QUERY_TRANSLATION_LANG", "Japanese")
SUMMARY_TARGET_LANG = os.getenv("SUMMARY_TARGET_LANG", "English")
BS_PARSER = os.getenv("BS_PARSER", "html.parser")
BS_TAGS_TO_REMOVE = os.getenv("BS_TAGS_TO_REMOVE", "script,style,noscript").split(',')
TEXT_SEPARATOR = os.getenv("TEXT_SEPARATOR", "\n")
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
TEMPLATE_INDEX = os.getenv("TEMPLATE_INDEX", "index.html")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

# Prompt templates (customizable to avoid hardcoding instructions)
TRANSLATION_PROMPT_TEMPLATE = os.getenv(
    "TRANSLATION_PROMPT_TEMPLATE",
    "Translate the following text into {target_lang}. ONLY output the translated text:\n\n{text}\n\nTranslation:"
)

SUMMARY_PROMPT_TEMPLATE = os.getenv(
    "SUMMARY_PROMPT_TEMPLATE",
    "Summarize the following in {summary_lang}:\n\n{text}\n\nSummary:"
)

# Form keys and route (customizable)
FORM_QUERY_KEY = os.getenv("FORM_QUERY_KEY", "query")
FORM_COMM_LANG_KEY = os.getenv("FORM_COMM_LANG_KEY", "comm_lang")
ROUTE_INDEX = os.getenv("ROUTE_INDEX", "/")

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
    prompt = TRANSLATION_PROMPT_TEMPLATE.format(target_lang=target_lang, text=text)
    return call_llama(prompt)


def google_search(query, gl=DEFAULT_COUNTRY, hl=DEFAULT_LANG):
    """
    Calls Google Custom Search API with location and language-based filtering.
    """
    url = GOOGLE_SEARCH_API_URL
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
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, BS_PARSER)
        for tag in soup(BS_TAGS_TO_REMOVE):
            tag.decompose()
        return soup.get_text(separator=TEXT_SEPARATOR)[:MAX_TEXT_LENGTH]
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


@app.route(ROUTE_INDEX, methods=["GET", "POST"])
def index():
    results, summary = [], ""
    if request.method == "POST":
        query = request.form.get(FORM_QUERY_KEY)
        comm_lang = request.form.get(FORM_COMM_LANG_KEY, DEFAULT_LANG)
        if query:
            # Translate the query using the configurable target language
            translated_query = llama_translate(query, QUERY_TRANSLATION_LANG)
            search_results = google_search(translated_query)
            # Build a dictionary of articles from search results
            articles = {
                result.get("title"): result.get("snippet")
                for result in search_results
                if result.get("title") and result.get("snippet")
            }
            prompt = TEXT_SEPARATOR.join(
                [f"{i}. {title}: {snippet}" for i, (title, snippet) in enumerate(articles.items(), start=1)]
            )
            # Translate the aggregated prompt into the community language
            translated_text = llama_translate(prompt, comm_lang)
            # Build the summary prompt using the configurable summary target language
            summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(summary_lang=SUMMARY_TARGET_LANG, text=translated_text)
            summary = call_llama(summary_prompt)
            results = search_results
    return render_template(TEMPLATE_INDEX, results=results, summary=summary)


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG)
