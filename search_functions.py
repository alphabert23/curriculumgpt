# research project
import requests
from gpt_functions import *
import streamlit as st

try:
    SERP_KEYS = [data['SERP_API_KEY'],data['SERP_API_KEY_2'],data['SERP_API_KEY_3']]
except:
    SERP_KEYS = [st.secrets['SERP_API_KEY'],
                 st.secrets['SERP_API_KEY_2'],
                 st.secrets['SERP_API_KEY_3']]

# Input search queries to search in Google Scholar
def search_google_scholar(query, num_results=3,language = 'en',as_ylo = 2020):
    """
    Params:
    query (str): The search query
    num_results (int): Number of results to return
    language (str): Two-letter code for desired language (i.e. "en" for English, "tl" for Tagalog/Filipino)
    as_ylo (int): The year of the last publication to be returned
    """
    for api_key in SERP_KEYS:
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
            print(f"Failed to retrieve data for API KEY {i}:", response.status_code)
            i+=1


