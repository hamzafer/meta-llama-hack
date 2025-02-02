#!/usr/bin/env python3
import os

import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Core configuration (overridable via environment variables)
API_KEY = os.getenv("API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
LLAMA_API_URL = os.getenv("LLAMA_API_URL", "http://localhost:11435/api/generate")
LLAMA_MODEL = os.getenv("LLAMA_MODEL", "llama3.3")
DEFAULT_LANG = os.getenv("DEFAULT_LANG", "en")  # fallback language if country not found
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "us")
GOOGLE_SEARCH_API_URL = os.getenv("GOOGLE_SEARCH_API_URL", "https://www.googleapis.com/customsearch/v1")
BS_PARSER = os.getenv("BS_PARSER", "html.parser")
BS_TAGS_TO_REMOVE = os.getenv("BS_TAGS_TO_REMOVE", "script,style,noscript").split(',')
TEXT_SEPARATOR = os.getenv("TEXT_SEPARATOR", "\n")
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "5"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")  # not used in Streamlit

# Prompt templates (customizable)
TRANSLATION_PROMPT_TEMPLATE = os.getenv(
    "TRANSLATION_PROMPT_TEMPLATE",
    "Translate the following text into {target_lang}. ONLY output the translated text:\n\n{text}\n\nTranslation:"
)
SUMMARY_PROMPT_TEMPLATE = os.getenv(
    "SUMMARY_PROMPT_TEMPLATE",
    "Summarize the following in {summary_lang}:\n\n{text}\n\nSummary:"
)

# Supported countries for the dropdown menu
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
    "jp": "jp",  # Japanese (adjust if needed; sometimes "ja" is preferred)
    "fr": "fr",
    "de": "de"
}


def call_llama(prompt: str) -> str:
    """
    Calls the Llama model via a local API.
    """
    st.write("**DEBUG: Calling Llama with prompt:**")
    st.text(prompt)
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
        st.write("**DEBUG: Received response from Llama:**")
        st.text(llama_response)
        return llama_response
    except requests.RequestException as e:
        error_msg = f"Error calling Llama: {e}"
        st.write("**DEBUG:**", error_msg)
        return error_msg


def llama_translate(text: str, target_lang: str) -> str:
    """
    Uses Llama to translate text into the target language.
    """
    st.write("**DEBUG: Translating text:**")
    st.text(text)
    st.write(f"**DEBUG: Target language:** {target_lang}")
    prompt = TRANSLATION_PROMPT_TEMPLATE.format(target_lang=target_lang, text=text)
    st.write("**DEBUG: Translation prompt being sent to Llama:**")
    st.text(prompt)
    translation = call_llama(prompt)
    st.write("**DEBUG: Translation result:**")
    st.text(translation)
    return translation


def google_search(query, gl=DEFAULT_COUNTRY, hl=DEFAULT_LANG):
    """
    Calls Google Custom Search API with location and language-based filtering.
    """
    st.write("**DEBUG: Performing Google search.**")
    st.write(f"**DEBUG: Query:** {query}")
    st.write(f"**DEBUG: Country (gl):** {gl}")
    st.write(f"**DEBUG: Language (hl):** {hl}")
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
            st.write("**DEBUG: Google API Error:**", results["error"])
            return []
        # Return only the top 10 results
        items = results.get("items", [])[:10]
        st.write("**DEBUG: Google search results fetched:**")
        for i, item in enumerate(items, start=1):
            st.write(f"Result {i}: Title: {item.get('title')}, Link: {item.get('link')}")
        return items
    except requests.RequestException as e:
        st.write("**DEBUG: Google API Exception:**", e)
        return []


def get_webpage_text(url: str) -> str:
    """
    Fetches webpage content and extracts text.
    """
    st.write(f"**DEBUG: Fetching webpage text from URL:** {url}")
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, BS_PARSER)
        for tag in soup(BS_TAGS_TO_REMOVE):
            tag.decompose()
        webpage_text = soup.get_text(separator=TEXT_SEPARATOR)[:MAX_TEXT_LENGTH]
        st.write("**DEBUG: Extracted webpage text:**")
        st.text(webpage_text)
        return webpage_text
    except requests.RequestException as e:
        error_msg = f"Error fetching {url}: {e}"
        st.write("**DEBUG:**", error_msg)
        return ""


def main():
    st.title("Local Search & Summarization Demo")
    st.write(
        "Enter your query and select a country. The app will automatically translate your query into the country's language before fetching and summarizing results.")

    # Get user input
    query = st.text_input("Enter your query:")

    # Create a list of country codes and names for the selectbox
    country_options = {country["code"]: country["name"] for country in supported_countries}
    # Display the country names, but store the country code
    selected_country = st.selectbox("Select your country:", options=list(country_options.keys()),
                                    format_func=lambda code: country_options[code])

    if st.button("Search"):
        st.write("**DEBUG: Received input**")
        st.write(f"User entered query: {query}")
        st.write(f"User selected country: {selected_country}")

        # Determine the target language based on selected country
        comm_lang = country_to_language.get(selected_country, DEFAULT_LANG)
        st.write(f"**DEBUG: Determined translation language:** {comm_lang}")

        if query:
            # Translate the query into the country's language
            st.write("**DEBUG: Translating the query...**")
            translated_query = llama_translate(query, comm_lang)
            st.write("**DEBUG: Translated query:**")
            st.text(translated_query)

            # Call Google Search API with the translated query
            st.write("**DEBUG: Calling Google Search API with the translated query...**")
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

            # Display the search results
            st.subheader("Top 10 Results")
            for idx, result in enumerate(results, start=1):
                st.markdown(f"**{idx}. {result['title']}**")
                st.write(result['snippet'])
                st.write(f"[Link]({result['link']})")
                if result['image_url']:
                    st.image(result['image_url'], width=150)
                st.write("---")

            st.write("**DEBUG: Fetched search results. Aggregating text for summarization...**")
            # Create an aggregated text for summarization
            aggregated_text = TEXT_SEPARATOR.join(
                [f"{i}. {title}: {snippet}" for i, (title, snippet) in enumerate(articles.items(), start=1)]
            )
            st.write("**DEBUG: Aggregated text:**")
            st.text(aggregated_text)

            # Translate aggregated text for summarization into the country's language
            st.write("**DEBUG: Translating aggregated text for summarization...**")
            translated_text = llama_translate(aggregated_text, comm_lang)
            st.write("**DEBUG: Translated aggregated text:**")
            st.text(translated_text)

            # Build the summary prompt and get the summary
            summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(summary_lang=comm_lang, text=translated_text)
            st.write("**DEBUG: Summary prompt being sent to Llama:**")
            st.text(summary_prompt)
            summary = call_llama(summary_prompt)
            st.write("**DEBUG: Final summary:**")
            st.text(summary)


if __name__ == "__main__":
    main()
