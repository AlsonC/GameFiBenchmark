import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# Define the URL and parameters for the Bitcoin market cap data
bitcoin_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart"
bitcoin_params = {
    'id': '1',  # Bitcoin's ID
    'range': 'all'
}

try:
    # Request the Bitcoin market cap data
    bitcoin_response = requests.get(bitcoin_url, params=bitcoin_params)
    bitcoin_response.raise_for_status()
    bitcoin_data = bitcoin_response.json()
    print("Bitcoin Data:")
    print(bitcoin_data)
    
    # Check if the data contains the expected structure
    if 'data' in bitcoin_data and 'points' in bitcoin_data['data']:
        bitcoin_points = bitcoin_data['data']['points']
        bitcoin_df = pd.DataFrame.from_dict(bitcoin_points, orient='index')
        bitcoin_df['timestamp'] = pd.to_datetime(bitcoin_df.index.astype(float), unit='s')  # Corrected to 's'
        
        # Rename and clean the market cap column
        if 'v' in bitcoin_df.columns:
            bitcoin_df = bitcoin_df.rename(columns={'v': 'marketCap'})
            bitcoin_df['marketCap'] = bitcoin_df['marketCap'].apply(lambda x: x if isinstance(x, (int, float)) else (x[0] if isinstance(x, list) and len(x) > 0 else None))  # Correct extraction
        bitcoin_df['marketCap'] = pd.to_numeric(bitcoin_df['marketCap'], errors='coerce') / 1e9  # Ensure numeric conversion
        
        # Filter data to start from 2020-07-01
        bitcoin_df = bitcoin_df[bitcoin_df['timestamp'] >= '2020-07-01']
        
        # Plot Bitcoin market cap on a new y-axis
        fig, ax1 = plt.subplots(figsize=(12, 8))  # Create a new figure and axis
        ax3 = ax1.twinx()
        ax3.plot(bitcoin_df['timestamp'], bitcoin_df['marketCap'],
                label='Bitcoin Market Cap', color='orange', linewidth=2)
        ax3.set_ylabel('Bitcoin Market Cap (Billions USD)')
        ax3.grid(False)  # Disable grid for the third y-axis

        # Customize the plot
        ax1.set_title('Bitcoin Market Cap History')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Market Cap (Billions USD)')
        ax1.grid(True)

        # Add legend
        ax3.legend(loc='upper left')

        # Rotate x-axis labels and format dates
        plt.xticks(rotation=45)
        ax1.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d/%y'))

        # Adjust layout
        plt.tight_layout()

        # Display the plot
        plt.show()

except Exception as e:
    print(f"Error getting Bitcoin market cap data: {e}")
