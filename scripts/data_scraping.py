import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from datetime import datetime


def check_scraping_date(airline, date):
    latest_file = sorted(os.listdir(f'../data/{airline}/raw'))[-1]
    latest_date = latest_file[5:15]
    return datetime.strptime(latest_date, '%Y-%m-%d') > datetime.strptime(date, '%Y-%m-%d')


def data_scraping(airline='british-airways', pages=30):
    base_url = f"https://www.airlinequality.com/airline-reviews/{airline}"
    # pages = 30
    page_size = 100
    reviews_data = []

    for page in range(1, pages+1):
        print(f"Scraping page {page}")
        url = f"{base_url}/page/{page}/?sortby=post_date%3ADesc&pagesize={page_size}"
        response = requests.get(url)
        content = response.content

        soup = BeautifulSoup(content, 'html.parser')

        # Extract each review container
        for review in soup.find_all("article", class_="comp_media-review-rated"):
            # dictionary to hold the review data
            review_data = {}

            # Get publish date
            publish_date = review.find("time").get("datetime") if review.find("time") else None
            if check_scraping_date(airline, publish_date):
                break

            review_data["publish_date"] = publish_date
            # Get header
            review_data["header"] = review.find("h2", class_="text_header").text.strip() \
                if review.find("h2", class_="text_header") else None

            # Get review text
            review_data["review_text"] = review.find("div", class_="text_content").text.strip() \
                if review.find("div", class_="text_content") else None

            # Extract individual attributes
            attributes = review.find("table", class_="review-ratings")
            for row in attributes.find_all("tr"):
                header = row.find("td", class_="review-rating-header").text.strip()
                value = row.find("td", class_="review-value").text.strip() if row.find("td", class_="review-value") else None
                stars = len(row.find_all("span", class_="star fill")) if row.find("td", class_="review-rating-stars") else None

                # Store the attribute
                if value:
                    review_data[header] = value
                elif stars is not None:
                    review_data[header] = stars

            # Append review data to list
            reviews_data.append(review_data)

    reviews_df = pd.DataFrame(reviews_data)
    if not os.path.exists(f'../data/{airline}/raw/'):
        os.makedirs(f'../data/{airline}/raw/')

    today = datetime.today().strftime('%Y-%m-%d')
    reviews_df.to_csv(f'../data/{airline}/raw/data_{today}.csv')


# if __name__ == '__main__':
#     data_scraping(pages=40)
