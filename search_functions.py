# research project
import requests
from xml.etree import ElementTree as ET
from bs4 import BeautifulSoup
from gpt_functions import *
import json
import os
import re

data = toml.load("api_keys.toml")
serper_api_key = data['SERPAPI_KEY']
brwoserless_api_key = data['BROWSERLESS_API_KEY']

def find_urls(text):
    # Regex pattern to find URLs (http, https, www)
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+|www\.(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    
    # Find all matches in the text and return them
    urls = re.findall(url_pattern, text)
    return urls

def read_file_as_string(file_path):
    """Reads the content of a file and returns it as a string."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def fetch_page_content(url, max_length):
    url = url.strip()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Determine the parser type based on URL or content-type
            if url.lower().endswith('.xml') or 'xml' in response.headers.get('Content-Type', ''):
                parser = 'xml'
            else:
                parser = 'html.parser'
            
            soup = BeautifulSoup(response.content, parser)
            
            # Define the tags you want to include
            desired_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']

            # Extracting the text within the specified tags
            extracted_texts = []
            seen_texts = set()  # Set to track texts that have already been added

            for tag in soup.find_all(desired_tags):
                text = tag.text.strip()
                if text and text not in seen_texts:  # Check if text is not empty and not seen before
                    clean_tag = f"<{tag.name}> {text} </{tag.name}>"  # Constructing tag string manually
                    extracted_texts.append(clean_tag)
                    seen_texts.add(text)  # Add text to the set of seen texts

            # Handling for div tags to include only the innermost with text
            for div_tag in soup.find_all('div'):
                text = div_tag.text.strip()
                if text and not div_tag.find('div') and text not in seen_texts:  # No inner div tags and has text not seen before
                    clean_div = f"<div> {text} </div>"  # Constructing div string manually
                    extracted_texts.append(clean_div)
                    seen_texts.add(text)  # Add text to the set of seen texts

            # Convert the list of texts to a single string and trim it to the maximum length
            extracted_texts = '\n'.join(extracted_texts)[:max_length]

            hyperlinks = [a.get('href') for a in soup.find_all('a', href=True) if 'http' in a.get('href')]

            return extracted_texts,hyperlinks

        else:
            print(f"Failed to retrieve page {url}: {response.status_code}\n{response.text}")
    except Exception as e:
        print(f"Error fetching page content: {e}")      

# 2. Store the information in data source

def generate_queries(course_details, numnber_of_queries=5):
    prompt = f"""{course_details}\n\nProvided are details regarding a course outline for which we need to look for references. 
Generate {numnber_of_queries} queries to search in Google Scholar to look for potential academic resources to be used as reference materials for this course. 
Output only the queries one line at a time and nothing else."""
    queries = gpt_response(prompt,'gpt-4-1106-preview').replace('"',"")
    return queries

# Part 2
# Given a website we use Google SERP API to get competitor information
def search(query):
    url = "https://google.serper.dev/search"

    payload = json.dumps({
        "q": query
    })

    headers = {
        'X-API-KEY': data["SERP_API_KEY"],
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    json_response = json.loads(response.text)
    return json_response

# Input search queries to search in Google Scholar
def search_google_scholar(query, num_results=3,language = 'en',as_ylo = 2020):
    """
    Params:
    query (str): The search query
    num_results (int): Number of results to return
    language (str): Two-letter code for desired language (i.e. "en" for English, "tl" for Tagalog/Filipino)
    as_ylo (int): The year of the last publication to be returned
    """
    
    # Your SerpAPI key
    api_key = serper_api_key

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




