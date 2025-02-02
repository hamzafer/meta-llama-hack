#!/usr/bin/env python3
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, request, render_template

# Load environment variables from .env file
load_dotenv()

# Core configuration (can be overridden via environment variables)
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "http://localhost:11435/api/generate")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.3")
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "us")
GOOGLE_SEARCH_API_URL = os.getenv("GOOGLE_SEARCH_API_URL", "https://www.googleapis.com/customsearch/v1")
BS_PARSER = os.getenv("BS_PARSER", "html.parser")
BS_TAGS_TO_REMOVE = os.getenv("BS_TAGS_TO_REMOVE", "script,style,noscript").split(',')
TEXT_SEPARATOR = os.getenv("TEXT_SEPARATOR", "\n")
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
TEMPLATE_INDEX = os.getenv("TEMPLATE_INDEX", "index.html")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

# Prompt templates (customizable)
TRANSLATION_PROMPT_TEMPLATE = os.getenv(
    "TRANSLATION_PROMPT_TEMPLATE",
    "Translate the following text into {target_lang}. ONLY output the translated text:\n\n{text}\n\nTranslation:"
)
SUMMARY_PROMPT_TEMPLATE = os.getenv(
    "SUMMARY_PROMPT_TEMPLATE",
    "Summarize the following in {summary_lang}:\n\n{text}\n\nSummary:"
)

# Form field keys
FORM_QUERY_KEY = os.getenv("FORM_QUERY_KEY", "query")
FORM_COMM_LANG_KEY = os.getenv("FORM_COMM_LANG_KEY", "comm_lang")
FORM_COUNTRY_KEY = os.getenv("FORM_COUNTRY_KEY", "country")
ROUTE_INDEX = os.getenv("ROUTE_INDEX", "/")

app = Flask(__name__)

# Define supported countries and languages for the dropdown menus
supported_countries = [
    {"code": "us", "name": "United States"},
    {"code": "no", "name": "Norway"},
    {"code": "jp", "name": "Japan"},
    {"code": "fr", "name": "France"},
    {"code": "de", "name": "Germany"}
]

supported_languages = [
    {"code": "en", "name": "English"},
    {"code": "no", "name": "Norwegian"},
    {"code": "jp", "name": "Japanese"},
    {"code": "fr", "name": "French"},
    {"code": "de", "name": "German"}
]


def call_llama(prompt: str) -> str:
    """
    Calls the Llama model via a local API.
    """
    print("DEBUG: Calling Llama with prompt:")
    print(prompt)
    payload = {
        "model": LLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(LLAMA_API_URL, json=payload)
        response.raise_for_status()
        result_json = response.json()
        llama_response = result_json.get("response", "Error: No response from Llama")
        print("DEBUG: Received response from Llama:")
        print(llama_response)
        return llama_response
    except requests.RequestException as e:
        error_msg = f"Error calling Llama: {e}"
        print("DEBUG:", error_msg)
        return error_msg


def llama_translate(text: str, target_lang: str) -> str:
    """
    Uses Llama to translate text into the target language.
    """
    print("DEBUG: Translating text:")
    print(text)
    print(f"DEBUG: Target language: {target_lang}")
    prompt = TRANSLATION_PROMPT_TEMPLATE.format(target_lang=target_lang, text=text)
    print("DEBUG: Translation prompt being sent to Llama:")
    print(prompt)
    translation = call_llama(prompt)
    print("DEBUG: Translation result:")
    print(translation)
    return translation


def google_search(query, gl=DEFAULT_COUNTRY, hl=DEFAULT_LANG):
    """
    Calls Google Custom Search API with location and language-based filtering.
    """
    print("DEBUG: Performing Google search.")
    print(f"DEBUG: Query: {query}")
    print(f"DEBUG: Country (gl): {gl}")
    print(f"DEBUG: Language (hl): {hl}")
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
            print("DEBUG: Google API Error:", results["error"])
            return []
        # Return only the top 10 results
        items = results.get("items", [])[:10]
        print("DEBUG: Google search results fetched:")
        for i, item in enumerate(items, start=1):
            print(f"DEBUG: Result {i}: Title: {item.get('title')}, Link: {item.get('link')}")
        return items
    except requests.RequestException as e:
        print("DEBUG: Google API Exception:", e)
        return []


def get_webpage_text(url: str) -> str:
    """
    Fetches webpage content and extracts text.
    """
    print(f"DEBUG: Fetching webpage text from URL: {url}")
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, BS_PARSER)
        for tag in soup(BS_TAGS_TO_REMOVE):
            tag.decompose()
        webpage_text = soup.get_text(separator=TEXT_SEPARATOR)[:MAX_TEXT_LENGTH]
        print("DEBUG: Extracted webpage text:")
        print(webpage_text)
        return webpage_text
    except requests.RequestException as e:
        error_msg = f"Error fetching {url}: {e}"
        print("DEBUG:", error_msg)
        return ""


@app.route(ROUTE_INDEX, methods=["GET", "POST"])
def index():
    results = []
    summary = ""
    query = ""
    selected_country = DEFAULT_COUNTRY
    comm_lang = DEFAULT_LANG

    if request.method == "POST":
        query = request.form.get(FORM_QUERY_KEY, "")
        comm_lang = request.form.get(FORM_COMM_LANG_KEY, DEFAULT_LANG)
        selected_country = request.form.get(FORM_COUNTRY_KEY, DEFAULT_COUNTRY)

        print("DEBUG: Received form submission.")
        print(f"DEBUG: User entered query: {query}")
        print(f"DEBUG: User selected language: {comm_lang}")
        print(f"DEBUG: User selected country: {selected_country}")

        if query:
            # Translate the query to the user's language
            print("DEBUG: Translating the query...")
            translated_query = llama_translate(query, comm_lang)
            print("DEBUG: Translated query:")
            print(translated_query)

            # Call Google search API with the translated query, country, and language parameters
            print("DEBUG: Calling Google Search API with the translated query...")
            search_results = google_search(translated_query, gl=selected_country, hl=comm_lang)
            results = []
            articles = {}
            for result in search_results:
                title = result.get("title")
                snippet = result.get("snippet")
                link = result.get("link")
                # Try to get an image from the result (if available)
                image_url = None
                pagemap = result.get("pagemap", {})
                if "cse_image" in pagemap:
                    images = pagemap.get("cse_image")
                    if images and isinstance(images, list):
                        image_url = images[0].get("src")
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link,
                    "image_url": image_url
                })
                if title and snippet:
                    articles[title] = snippet

            print("DEBUG: Fetched search results. Aggregating text for summarization...")
            # Create an aggregated text for summarization
            aggregated_text = TEXT_SEPARATOR.join(
                [f"{i}. {title}: {snippet}" for i, (title, snippet) in enumerate(articles.items(), start=1)]
            )
            print("DEBUG: Aggregated text:")
            print(aggregated_text)

            # Translate aggregated text into the user's language
            print("DEBUG: Translating aggregated text for summarization...")
            translated_text = llama_translate(aggregated_text, comm_lang)
            print("DEBUG: Translated aggregated text:")
            print(translated_text)

            # Build the summary prompt using the same language
            summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(summary_lang=comm_lang, text=translated_text)
            print("DEBUG: Summary prompt being sent to Llama:")
            print(summary_prompt)
            summary = call_llama(summary_prompt)
            print("DEBUG: Final summary:")
            print(summary)

    return render_template(
        TEMPLATE_INDEX,
        results=results,
        summary=summary,
        query=query,
        selected_country=selected_country,
        comm_lang=comm_lang,
        supported_countries=supported_countries,
        supported_languages=supported_languages
    )


if __name__ == "__main__":
    print("DEBUG: Starting Flask app.")
    app.run(debug=FLASK_DEBUG)
