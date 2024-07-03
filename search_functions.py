# research project
import requests
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from gpt_functions import *
import json
import re

try:
    data = toml.load("api_keys.toml")
    SERPER_API_KEY = data['SERPAPI_KEY']
except:
    SERPER_API_KEY = ""

# Input search queries to search in Google Scholar
def search_google_scholar(query, num_results=3,language = 'en',as_ylo = 2020,api_key = SERPER_API_KEY):
    """
    Params:
    query (str): The search query
    num_results (int): Number of results to return
    language (str): Two-letter code for desired language (i.e. "en" for English, "tl" for Tagalog/Filipino)
    as_ylo (int): The year of the last publication to be returned
    """
    

    # Set up the search parameters
    params = {
        "engine": "google_scholar",
        "q": query,  # Your search query
        "api_key": api_key,
        "as_ylo": as_ylo,
        "hl":language,
        'num': num_results
    }

    # Make the API request
    response = requests.get("https://serpapi.com/search", params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        results = response.json()
        return results
    else:
        print("Failed to retrieve data:", response.status_code)
        return None

# Build queries 
# Do Search and retrieve results
def fetch_site_content(url, max_length=1000):
    """Fetch and parse the content and hyperlinks of a web page."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract the text
            text = soup.get_text(separator=' ', strip=True)
            
            # Find all hyperlinks in the page
            hyperlinks = [a.get('href') for a in soup.find_all('a', href=True) if 'http' in a.get('href')]

            return text[:max_length], hyperlinks
        else:
            print(f"Failed to retrieve page: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Error fetching page content: {e}")
        return None, None




