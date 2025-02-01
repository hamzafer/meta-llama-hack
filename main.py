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

app = Flask(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
search_engine_id = os.getenv("SEARCH_ENGINE_ID")

def call_llama(prompt: str) -> str:
    """
    Calls the Llama3.3:70b model via a local API running on your GPU.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.3:70b",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an error for bad responses
        result_json = response.json()
        return result_json.get("response", "Error: No response from Llama3.3")
    except requests.RequestException as e:
        return f"Error calling Llama3.3: {e}"

def llama_translate(text: str, target_lang: str) -> str:
    """
    Uses Llama3.3 (Ollama) to translate text into the target language.
    """
    prompt = f"Translate the following text into {target_lang}. ONLY output the translated text:\n\n{text}\n\nTranslation:"
    return call_llama(prompt)

def google_search(query, gl="no", hl="no"):
    """
    Calls Google Custom Search API with location and language-based filtering.
    - `gl`: Country code (e.g., "no" for Norway).
    - `hl`: Language hint (e.g., "no" for Norwegian).
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "gl": gl,  # Country location
        "hl": hl   # Language hint
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()

        if "error" in results:
            print("Google API Error:", results["error"])
            return []  # Return empty list if there's an error

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
        
        # Remove unnecessary elements
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        
        return soup.get_text(separator="\n")[:1000]  # Limit to first 1000 characters
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

@app.route("/", methods=["GET", "POST"])
def index():
    results, summary = [], ""

    if request.method == "POST":
        query = request.form.get("query")
        comm_lang = request.form.get("comm_lang", "en")  # Default to English

        if query:
            # Translate query to Norwegian for better search results
            translated_query = llama_translate(query, "Norwegian")

            # Perform Google Search
            search_results = google_search(translated_query)

            # Extract title and snippet
            articles = {result.get("title"): result.get("snippet") for result in search_results if result.get("title") and result.get("snippet")}

            # Prepare summarization prompt
            prompt = "\n".join([f"{i}. {title}: {snippet}" for i, (title, snippet) in enumerate(articles.items(), start=1)])

            # Translate results back to the user's language
            translated_text = llama_translate(prompt, comm_lang)

            # Summarize the results
            summary_prompt = f"Summarize the following in English:\n\n{translated_text}\n\nSummary:"
            summary = call_llama(summary_prompt)

            results = search_results

    return render_template("index.html", results=results, summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
