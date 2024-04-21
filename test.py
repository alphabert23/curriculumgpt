import streamlit as st
import requests
from bs4 import BeautifulSoup

def scrape_site(url):
    try:
        # Fetch content from URL
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses

        # Use Beautiful Soup to parse and extract information
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    st.title("Simple Web Scraper App")
    
    # Text input for URL
    url = st.text_input("Enter the URL you want to scrape", "")

    if st.button("Scrape"):
        if url:
            result = scrape_site(url)
            st.text_area("Scraped Content:", value=result, height=300)
        else:
            st.write("Please enter a URL to scrape.")

if __name__ == "__main__":
    main()
