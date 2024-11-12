import requests
import matplotlib.pyplot as plt
from datetime import datetime

def plot_bitcoin_price():
    """
    Fetches live Bitcoin price data and plots it.
    """
    # Define API endpoint and parameters
    bitcoin_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical"
    bitcoin_params = {
        'id': 1,  # Bitcoin's ID on CoinMarketCap
        'convert': 'USD',
        'range': 'all'
    }

    # Fetch Bitcoin price data
    try:
        bitcoin_response = requests.get(bitcoin_url, params=bitcoin_params)
        bitcoin_response.raise_for_status()
        bitcoin_data = bitcoin_response.json().get('data', {}).get('quotes', [])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Bitcoin price data: {e}")
        return

    # Convert timestamps to datetime objects
    try:
        bitcoin_timestamps = [datetime.fromtimestamp(float(data['timestamp']) / 1000) for data in bitcoin_data]
        bitcoin_prices = [float(data['quote']['USD']['price']) for data in bitcoin_data]
    except KeyError as e:
        print(f"Error processing Bitcoin price data: Missing key {e}")
        return

    # Filter data for the years 2021 to 2024
    bitcoin_timestamps_filtered = [timestamp for timestamp in bitcoin_timestamps if 2021 <= timestamp.year <= 2024]
    bitcoin_prices_filtered = [bitcoin_prices[i] for i in range(len(bitcoin_timestamps)) if 2021 <= bitcoin_timestamps[i].year <= 2024]

    # Plotting
    fig, ax1 = plt.subplots(figsize=(12, 8))

    ax1.plot(bitcoin_timestamps_filtered, bitcoin_prices_filtered, label='Bitcoin Price 2021-2024', color='orange', alpha=0.5)

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Bitcoin Price (USD)', color='orange')

    ax1.tick_params(axis='y', labelcolor='orange')

    fig.tight_layout()
    plt.title('Bitcoin Price from 2021 to 2024')
    plt.show()

# Call the function to plot the data
plot_bitcoin_price()
