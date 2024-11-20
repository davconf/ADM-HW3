# crawler.py
import requests
from bs4 import BeautifulSoup
import os

def get_restaurant_urls(soup):

    # Extracts restaurant URLs from the BeautifulSoup object.

    restaurant_urls = []
    for link in soup.find_all('a', class_='link'):
        href = link.get('href')
        # CONDITIONS TO IDENTIFY INDIVIDUAL RESTAURANT URLS
        # Checks if the href exists and contains the string "/restaurant/"
        # Checks if the URL has exactly five forward slashes
        if href and "/restaurant/" in href and href.count('/') == 5:
            restaurant_urls.append(href)
    return restaurant_urls


def download_restaurants_html_pages(input_file, directory_path):
    
    # Downloads HTML pages for each restaurant URL in the input file.
    
    with open(input_file, 'r') as f:
        for line in f:
            page_num, url = line.strip().split(',')

            try:
                response = requests.get(url)
                response.raise_for_status()

                folder_name = os.path.join(directory_path, str(page_num))
                os.makedirs(folder_name, exist_ok=True) # exist_ok=True prevents error if the directory already exists

                # Extract the restaurant name from the URL for the filename
                restaurant_name = url.split('/')[-1]
                filename = os.path.join(folder_name, f"{restaurant_name}.html")

                with open(filename, 'w', encoding='utf-8') as html_file:
                    html_file.write(response.text)

                print(f"Downloaded {url} to {filename}")

            except requests.exceptions.RequestException as e:
                print(f"Error downloading {url}: {e}")