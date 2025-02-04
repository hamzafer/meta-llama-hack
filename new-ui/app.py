#!/usr/bin/env python3
import os
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend requests

# Load environment variables from .env file
load_dotenv()

USE_STATIC_RESULTS = os.getenv("USE_STATIC_RESULTS", "True").lower() in ("true", "1", "t")

# Core configuration (overridable via environment variables)
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "http://localhost:11434/api/generate")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.3:70b")
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")  # fallback language if country not found
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "no")
GOOGLE_SEARCH_API_URL = os.getenv("GOOGLE_SEARCH_API_URL", "https://www.googleapis.com/customsearch/v1")
BS_PARSER = os.getenv("BS_PARSER", "html.parser")
BS_TAGS_TO_REMOVE = os.getenv("BS_TAGS_TO_REMOVE", "script,style,noscript").split(',')
TEXT_SEPARATOR = os.getenv("TEXT_SEPARATOR", "\n")
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

# New form field and default for summary language
FORM_SUMMARY_LANG_KEY = os.getenv("FORM_SUMMARY_LANG_KEY", "summary_lang")
DEFAULT_SUMMARY_LANG = os.getenv("DEFAULT_SUMMARY_LANG", DEFAULT_LANG)

# Prompt templates (customizable)
TRANSLATION_PROMPT_TEMPLATE = os.getenv(
    "TRANSLATION_PROMPT_TEMPLATE",
    "Translate the following text into {target_lang}. ONLY output the translated text:\n\n{text}\n\nTranslation:"
)
SUMMARY_PROMPT_TEMPLATE = os.getenv(
    "SUMMARY_PROMPT_TEMPLATE",
    "Summarize the following in {summary_lang}:\n\n{text}\n\nSummary:"
)

# Form field keys for the query and country
FORM_QUERY_KEY = os.getenv("FORM_QUERY_KEY", "query")
FORM_COUNTRY_KEY = os.getenv("FORM_COUNTRY_KEY", "country")
ROUTE_INDEX = os.getenv("ROUTE_INDEX", "/")

app = Flask(__name__)

# Supported countries for the dropdown menu (still useful for the API)
supported_countries = [
    {"code": "us", "name": "United States"},
    {"code": "no", "name": "Norway"},
    {"code": "jp", "name": "Japan"},
    {"code": "fr", "name": "France"},
    {"code": "de", "name": "Germany"}
]

# Mapping from country code to language code
country_to_language = {
    "us": "en",
    "no": "no",  # Norwegian
    "jp": "jp",  # Japanese (adjust if you need "ja")
    "fr": "fr",
    "de": "de"
}


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
    If USE_STATIC_RESULTS is True, return the static (pre-defined) results.
    """
    if USE_STATIC_RESULTS:
        print("DEBUG: Returning static search results.")
        static_results = [
            {
                "title": "Trikk krasjet i Oslo: Føreren er siktet",
                "snippet": "Resultat fra VG: Trikk krasjet i Oslo med siktet fører. Fire skadde.",
                "link": "https://www.vg.no/nyheter/i/vgxjaX/trikk-krasjet-i-butikk-i-oslo-trikkefoereren-er-siktet",
                "image_url": None
            },
            {
                "title": "Trikk, Ulykke | Trikk krasjet inn i Eplehuset i Storgata",
                "snippet": "Resultat fra ao.no: Trikk krasjet inn i Eplehuset i Storgata.",
                "link": "https://www.ao.no/trikki-butikk-i-storgata/s/5-128-914143",
                "image_url": None
            },
            {
                "title": "Trikkeulykken i Oslo henlegges – Stor-Oslo",
                "snippet": "Resultat fra NRK: Trikkeulykken i Oslo henlegges.",
                "link": "https://www.nrk.no/stor-oslo/trikkeulykken-i-oslo-henlegges-1.17178415",
                "image_url": None
            },
            {
                "title": "Oslo trikkulykke. Mannen ble hardt skadet",
                "snippet": "Resultat fra Wataha: Oslo trikkulykke med hardt skadet mann.",
                "link": "https://wataha.no/no/2021/10/05/oslo-wypadek-tramwajowy-mezczyzna-ciezko-ranny/",
                "image_url": None
            },
            {
                "title": "Trikkeulykken i Storgata – Stor-Oslo",
                "snippet": "Resultat fra NRK: Trikkeulykken i Storgata.",
                "link": "https://www.nrk.no/stor-oslo/trikkeulykken-i-storgata-1.17104779",
                "image_url": None
            },
            {
                "title": "Trikk, Ulykke | Person påkjørt av trikk i Oslo",
                "snippet": "Resultat fra Nettavisen: Person påkjørt av trikk i Oslo.",
                "link": "https://www.nettavisen.no/nyheter/person-pakjort-av-trikk-i-oslo/s/12-95-3423942827",
                "image_url": None
            },
            {
                "title": "Trikk sporet av og krasjet inn i butikk i Oslo sentrum: Fire personer ...",
                "snippet": "Resultat fra Inyheter: Trikk sporet av og krasjet inn i butikk i Oslo sentrum.",
                "link": "https://inyheter.no/29/10/2024/trikk-sporet-av-og-krasjet-inn-i-butikk-i-oslo-sentrum-fire-personer-skadet/",
                "image_url": None
            },
            {
                "title": "Trikkeulykken i Storgata – Wikipedia",
                "snippet": "Resultat fra Wikipedia: Informasjon om trikkeulykken i Storgata.",
                "link": "https://no.wikipedia.org/wiki/Trikkeulykken_i_Storgata",
                "image_url": None
            },
            {
                "title": "Avisa Oslo | Den lille taco-trucken i Schweigaards gate blir omfavnet ...",
                "snippet": "Resultat fra Instagram: Den lille taco-trucken i Schweigaards gate.",
                "link": "https://www.instagram.com/avisaoslo/reel/C-MtkbRo80h/",
                "image_url": None
            },
            {
                "title": "Trikkeulykken i Oslo: Politiet henlegger saken: - Glad det ikke gikk ...",
                "snippet": "Resultat fra TV2: Politiet henlegger saken etter trikkulykke.",
                "link": "https://www.tv2.no/nyheter/politiet-henlegger-saken-glad-det-ikke-gikk-verre/17300477/",
                "image_url": None
            },
        ]
        return static_results

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


@app.route("/api/search", methods=["POST"])
def api_search():
    # Expect a JSON payload
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    query = data.get(FORM_QUERY_KEY, "")
    selected_country = data.get(FORM_COUNTRY_KEY, DEFAULT_COUNTRY)
    summary_lang = data.get(FORM_SUMMARY_LANG_KEY, DEFAULT_SUMMARY_LANG)
    results = []
    summary = ""

    print("DEBUG: Received API JSON request.")
    print(f"DEBUG: Query: {query}")
    print(f"DEBUG: Selected country: {selected_country}")
    print(f"DEBUG: Summary language: {summary_lang}")

    if query:
        comm_lang = country_to_language.get(selected_country, DEFAULT_LANG)
        print(f"DEBUG: Determined search translation language: {comm_lang}")

        # Translate the query
        translated_query = llama_translate(query, comm_lang)
        print("DEBUG: Translated query:")
        print(translated_query)

        # Get search results from Google Search API
        search_results = google_search(translated_query, gl=selected_country, hl=comm_lang)
        articles = {}
        for result in search_results:
            title = result.get("title")
            snippet = result.get("snippet")
            link = result.get("link")
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

        aggregated_text = TEXT_SEPARATOR.join(
            [f"{i}. {title}: {snippet}" for i, (title, snippet) in enumerate(articles.items(), start=1)]
        )
        print("DEBUG: Aggregated text:")
        print(aggregated_text)

        # Translate aggregated text into the summary language
        translated_text = llama_translate(aggregated_text, summary_lang)
        print("DEBUG: Translated aggregated text:")
        print(translated_text)

        # Parse translated text for title/snippet pairs using regex
        pattern = re.compile(r'\d+\.\s(.*?):\s(.*)')
        parsed_data = []
        for match in pattern.finditer(translated_text):
            parsed_data.append((match.group(1).strip(), match.group(2).strip()))

        for i, (title, snippet) in enumerate(parsed_data):
            if i < len(results):
                results[i]["title"] = title
                results[i]["snippet"] = snippet

        summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(summary_lang=summary_lang, text=translated_text)
        print("DEBUG: Summary prompt being sent to Llama:")
        print(summary_prompt)
        summary = call_llama(summary_prompt)
        print("DEBUG: Final summary:")
        print(summary)

    return jsonify({
        "query": query,
        "selected_country": selected_country,
        "summary_lang": summary_lang,
        "results": results,
        "summary": summary
    })


if __name__ == "__main__":
    print("DEBUG: Starting Flask API (JSON only).")
    app.run(debug=FLASK_DEBUG)
