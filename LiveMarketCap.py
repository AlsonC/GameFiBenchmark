import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from matplotlib.dates import DateFormatter

def get_gaming_market_cap():
    url = "https://api.coinmarketcap.com/data-api/v3/sector/w/market-chart"
    
    # Parameters for the request
    params = {
        'tagSlug': 'gaming',
        'range': 'all'
    }
    
    try:
        # Make the API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        # Add debug print to see the structure of the response
        # print("API Response structure:", data.keys())
        
        # Check if 'data' exists in the response
        if 'data' not in data:
            # print("Error: 'data' not found in API response")
            return
            
        # Check if 'marketCapPoints' exists in data
        if 'marketCapPoints' not in data['data']:
            # print("Error: 'marketCapPoints' not found in API response data")
            # print("Available keys in data:", data['data'].keys())
            return
            
        points = data['data']['marketCapPoints']
        
        # Convert to DataFrame
        df = pd.DataFrame(points)
        
        # Convert timestamp to datetime - handle string timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')
        
        # Rename 'value' column to 'marketCap' if that's what's in the response
        if 'value' in df.columns:
            df = df.rename(columns={'value': 'marketCap'})
        
        # Convert marketCap to billions for better readability
        df['marketCap'] = df['marketCap'] / 1e9
        
        # Create the plot
        plt.figure(figsize=(12, 6))
        plt.plot(df['timestamp'], df['marketCap'])
        
        # Customize the plot
        plt.title('Gaming Token Market Cap Over Time')
        plt.xlabel('Date')
        plt.ylabel('Market Cap (Billions USD)')
        plt.grid(True)
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Display the plot
        # plt.show()
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
    except KeyError as e:
        print(f"Error parsing API response: {e}")
        print("Full response:", data)  # Print full response for debugging
    except Exception as e:
        print(f"Unexpected error: {e}")

# Call the function
get_gaming_market_cap()

