import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from flask import Flask, request, render_template, send_file
import matplotlib.pyplot as plt
import io
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

def scrape_booking(city, checkin, checkout):
    base_url = "https://www.booking.com/searchresults.en-gb.html"
    params = {
        'ss': city,
        'ssne': city,
        'ssne_untouched': city,
        'checkin': checkin,
        'checkout': checkout,
        'group_adults': '2',
        'no_rooms': '1',
        'group_children': '0'
    }
    url = f"{base_url}?{urlencode(params)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    hotels = soup.find_all('div', {'data-testid': 'title'})
    prices = soup.find_all('span', {'data-testid': 'price-and-discounted-price'})
    original_prices = soup.find_all('span', {'class': 'e8acaa0d22 f018fa3636 d9315e4fb0'})
    ratings = soup.find_all('div', {'class': 'd0522b0cca fd44f541d8'})

    data = []
    for hotel, price, original_price, rating in zip(hotels, prices, original_prices, ratings):
        price_text = price.text.strip().replace('₹', '').replace(',', '').strip()
        original_price_text = original_price.text.strip().replace('₹', '').replace(',', '').strip()

        try:
            price_value = float(price_text)
            original_price_value = float(original_price_text)
        except ValueError:
            price_value = float('inf')
            original_price_value = float('inf')

        rating_text = rating.text.strip()
        rating_score = rating_text.split()[1] if len(rating_text.split()) > 1 else rating_text

        data.append({
            'Hotel Name': hotel.text.strip(),
            'Price': price_text,
            'Original Price': original_price_text,
            'Price Value': price_value,
            'Original Price Value': original_price_value,
            'Rating': rating_score,
            'Platform': 'Booking.com'
        })

    return data

def scrape_expedia(city, checkin, checkout):
    base_url = "https://www.expedia.com/Hotels"
    params = {
        'destination': city,
        'checkin_date': checkin,
        'checkout_date': checkout,
        'adults': '2',
        'rooms': '1',
        'children': '0'
    }
    url = f"{base_url}?{urlencode(params)}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    hotels = soup.find_all('div', {'class': 'hotel-card'})
    data = []
    for hotel in hotels:
        hotel_name = hotel.find('h3').text.strip()
        price_text = hotel.find('span', {'class': 'price'}).text.strip().replace('₹', '').replace(',', '').strip()
        try:
            price_value = float(price_text)
        except ValueError:
            price_value = float('inf')
        
        rating_text = hotel.find('span', {'class': 'rating'}).text.strip()
        data.append({
            'Hotel Name': hotel_name,
            'Price': price_text,
            'Price Value': price_value,
            'Rating': rating_text,
            'Platform': 'Expedia'
        })

    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        # Scrape data from both platforms
        booking_data = scrape_booking(city, checkin, checkout)
        expedia_data = scrape_expedia(city, checkin, checkout)

        # Combine the data
        all_data = booking_data + expedia_data

        # Sort combined data by price value
        sorted_data = sorted(all_data, key=lambda x: x['Price Value'])

        # Find the best deal
        if sorted_data:
            best_deal = min(sorted_data, key=lambda x: x['Price Value'])
        else:
            best_deal = None

        # Render the results page with the combined data
        return render_template('results.html', sorted_data=sorted_data, best_deal=best_deal)
    else:
        return render_template('index.html')
@app.route('/plot.png')
def plot():
    # Generate the data (for demonstration, using random data)
    original_prices = np.random.uniform(2000, 8000, 10)
    discounted_prices = original_prices * np.random.uniform(0.7, 0.9, 10)

    # Prepare the data for bar plot
    hotel_names = [f"Hotel {i+1}" for i in range(len(original_prices))]  # Dummy hotel names

    # Plotting
    plt.figure(figsize=(12, 8))
    bar_width = 0.35
    index = np.arange(len(hotel_names))

    # Plot original and discounted prices as bars
    plt.bar(index, original_prices, bar_width, color='blue', label='Original Price')
    plt.bar(index + bar_width, discounted_prices, bar_width, color='green', label='Discounted Price')

    plt.xlabel('Hotels')
    plt.ylabel('Price (INR)')
    plt.title('All Hotels Original vs Discounted Price Comparison')
    plt.xticks(index + bar_width / 2, hotel_names, rotation=45, ha="right")
    plt.legend()

    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.savefig(buf, format='png')
    buf.seek(0)

    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
