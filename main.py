#!/usr/bin/env python3
"""
Google Search API + Llama3.2 (Ollama) for Translation & Summarization.
- Uses Google Search API (with location-based search)
- Uses Llama3.2 (Ollama) for translations (query/result)
- Summarizes results with Llama3.2
"""

import os
import subprocess
import requests
from flask import Flask, request, render_template
from bs4 import BeautifulSoup
from dotenv import load_dotenv

app = Flask(__name__)

# Replace with your actual API Key and Search Engine ID
# API_KEY = os.environ.get("GOOGLE_SEARCH_API_KEY")  # Set in your environment
# SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")  # Set in your environment

# Load .env file
load_dotenv()

# Retrieve variables
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
        response.raise_for_status()  # Raises an error for bad status codes.
        print(response)
        print('\n\n/n\n')
        # Assume the API returns JSON with a 'text' field containing the result.
        result_json = response.json()
        return result_json["response"]
        # print(result_json["response"])
        # if "text" in result_json:
        #     print(result_json["response"]) # ["text"].strip().get)
        #     print(5/0)
        #     return result_json["text"].strip()
        # # If the expected field isn't present, return the whole JSON as a string.
        # return str(result_json)
    except requests.RequestException as e:
        return f"Error calling Llama3.3: {e}"
    

# def call_llama(prompt: str) -> str:
#     """
#     Calls the locally installed Llama3.2 model via Ollama’s CLI.
#     Used for both translation and summarization.
#     """
#     # try:
#     #     result = subprocess.run(
#     #         ["ollama", "run", "llama3.2", "--prompt", prompt],
#     #         capture_output=True, text=True, check=True
#     #     )
#     #     return result.stdout.strip()
#     # except subprocess.CalledProcessError as e:
#     #     return f"Error calling Llama3.2: {e}"
    

#     try:
#         # result = subprocess.run(
#         #     ["ollama", "run", "llama3.2"],
#         #     input=prompt,  # Pass the prompt as input
#         #     capture_output=True, text=True, check=True
#         # )
#         result = subprocess.run(
#             ["ollama", "run", "llama3.2"],
#             input=prompt,  # Pass the prompt as input
#             capture_output=True,
#             text=True,
#             encoding="utf-8",  # Force UTF-8 encoding
#             check=True
#         )
#         return result.stdout.strip()
#     except subprocess.CalledProcessError as e:
#         return f"Error calling Llama3.2: {e}"

def llama_translate(text: str, target_lang: str) -> str:
    """
    Uses Llama3.2 (Ollama) to translate text into the target language.
    """
    prompt = f"Translate the following text into {target_lang}, I want you TO ONLY OUTPUT THE TRANSLATED TEXT AND NOTHING ELSE:\n\n{text}\n\nTranslation:"
    return call_llama(prompt)

def google_search(query, gl="no", hl="no"):
    """
    Calls Google Custom Search API with location and language-based filtering.
    - `gl`: Country code (e.g., "no" for Norway).
    - `hl`: Language hint (e.g., "no" for Norwegian).
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": "AIzaSyCgYM01RkUmNKuc8-gf-wXkYPzG0REULgY",
        "cx": "8685ee9e6bd8b46dc",
        "q": query,
        "gl": gl,  # Country location
        "hl": hl   # Language hint
    }
    response = requests.get(url, params=params)

    try:
        results = response.json()
        print("API Response:", results)  # Debugging

        if "error" in results:
            print("Error:", results["error"])
            return []  # Return empty list if there's an error

        return results.get("items", [])

    except Exception as e:
        print("Exception:", e)
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
        return soup.get_text(separator="\n")[:1000]  # First 1000 characters
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    summary = ""
    # query = 'Tram Crash Oslo'
    # query = request.form.get("query")
    # comm_lang = request.form.get("comm_lang", "en")  # Default to English

    # comm_land = 'en'
    
    # if query:
    #     # Translate query to Norwegian using Llama3.2
    #     translated_query = llama_translate(query, "Norwegian")
    # print(123/0)
    if request.method == "POST":
        # query = 'Tram Crash Oslo'
        query = request.form.get("query")
        comm_lang = request.form.get("comm_lang", "en")  # Default to English

        # comm_land = 'en'
        
        if query:
            # Translate query to Norwegian using Llama3.2
            translated_query = llama_translate(query, "Norwegian")

            # translated_query = 'Trikk Ulykke i Oslo'

            # Perform Google Search in Norway
            search_results = google_search(translated_query)


            print('\n/n\n')
            print(search_results)
            print('/n/n')
            # print(search_results['snippet'])
            # print(5/0)

            # Ensure articles is a dictionary.
            articles = {}

            for result in search_results:
                title = result.get("title")
                snippet = result.get("snippet")
                if title and snippet:
                    articles[title] = snippet

            # print(articles)
            prompt = ""

            for i, (title, snippet) in enumerate(articles.items(), start=1):
                prompt += f"{i}. {title}: {snippet}\n"

            # print(prompt)

            #     for i, result in enumerate(search_results['items']):
            #         results.append(result)
            #         print(f"Result {i+1}: {result.get('snippet', 'No snippet available')}")  
            # else:
            #     print("No search results found.")



            # import json  # Only needed if the response is a JSON string


            # # Initialize an empty dictionary
            # title_snippet_dict = {}

            # # Check if "items" exist in the response
            # if 'items' in search_results and isinstance(search_results['items'], list):
            #     for result in search_results['items']:
            #         title = result.get('title', 'No Title')
            #         snippet = result.get('snippet', 'No Snippet')
                    
            #         # Add to dictionary
            #         title_snippet_dict[title] = snippet

            # Print the extracted dictionary
            # print(articles)



            # print(results)
            # print(5/0)
            translated_text = llama_translate(prompt, comm_lang)  # Translate back


            print(translated_text)

            combined_text = translated_text

            # print(5/0)


            # if results != []:
            #     combined_text = ""
            #     for result in search_results[:5]:  # Top 5 results
            #         url = result.get("link")
            #         if url:
            #             page_text = get_webpage_text(url)
            #             translated_text = llama_translate(page_text, comm_lang)  # Translate back
            #             combined_text += translated_text + "\n\n"

                # Summarize using Llama3.2
            # prompt = f"Summarize the following in {comm_lang}:\n\n{combined_text}\n\nSummary:"
            prompt = f"Summarize the following in English:\n\n{combined_text}\n\nSummary:"

            summary = call_llama(prompt)

            results = search_results

    return render_template("index.html", results=results, summary=summary)

if __name__ == "__main__":
    app.run(debug=True)
