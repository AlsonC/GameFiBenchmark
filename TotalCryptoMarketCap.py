import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# Get total gaming market cap data from API
url = "https://api.coinmarketcap.com/data-api/v3/sector/w/market-chart"
params = {
    'tagSlug': 'gaming',
    'range': 'all'
}

try:
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    
    if 'data' in data and 'marketCapPoints' in data['data']:
        points = data['data']['marketCapPoints']
        gaming_df = pd.DataFrame(points)
        gaming_df['timestamp'] = pd.to_datetime(gaming_df['timestamp'].astype(float), unit='ms')
        if 'value' in gaming_df.columns:
            gaming_df = gaming_df.rename(columns={'value': 'marketCap'})
        gaming_df['marketCap'] = gaming_df['marketCap'] / 1e9
        
        # Plot the total gaming market cap
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.plot(gaming_df['timestamp'], gaming_df['marketCap'], label='Total Gaming Market Cap', color='black', linewidth=2)
        ax.set_title('Total Gaming Market Cap History')
        ax.set_xlabel('Date')
        ax.set_ylabel('Gaming Market Cap (Billions USD)')
        ax.grid(True)
        ax.legend(loc='upper left')
        
        # Rotate x-axis labels and format dates
        plt.xticks(rotation=45)
        ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d/%y'))
        
        # Adjust layout
        plt.tight_layout()
        
        # Display the plot
        plt.show()

except Exception as e:
    print(f"Error getting gaming market cap data: {e}")
