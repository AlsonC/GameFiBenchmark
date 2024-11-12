import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import requests
from datetime import datetime

# Load the Excel file
file_path = r"C:/Users/theal/MakersFund/IndexProject/110824.xlsx"
df = pd.read_excel(file_path)

# Clean column names and convert FDV to numeric
df.columns = df.columns.str.strip()
df['FDV'] = pd.to_numeric(df['FDV'].replace({'\$': '', ',': ''}, regex=True))

# Filter for rows with FDV over 500 million
filtered_df = df[df['FDV'] > 500000000].copy()

# Extract token abbreviations
filtered_df['Token Abbreviation'] = filtered_df['Coin'].str.extract(r'\((.*?)\)')

# Dictionary to store DataFrames for each token
token_dfs = {}

# Read and process CSV files for each token
for token in filtered_df['Token Abbreviation']:
    try:
        csv_path = f"C:/Users/theal/MakersFund/IndexProject/Graphs/{token}_All_graph_coinmarketcap.csv"
        df = pd.read_csv(csv_path, sep=';')
        
        # Update timestamp parsing to handle ISO format with 'Z' timezone
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
        
        # Ensure marketCap is numeric and remove any potential invalid values
        df['marketCap'] = pd.to_numeric(df['marketCap'], errors='coerce')
        df = df.dropna(subset=['marketCap'])
        
        # Only store tokens that have valid data
        if not df.empty and df['marketCap'].max() > 0:
            token_dfs[token] = df
    except FileNotFoundError:
        print(f"Warning: No data file found for {token}")
    except Exception as e:
        print(f"Error processing {token}: {str(e)}")

# Add a check to ensure we have data
if not token_dfs:
    raise ValueError("No data was loaded successfully. Please check the CSV files and their formats.")

# Create cohort periods (12-month intervals) with UTC timezone
cohort_periods = pd.date_range(
    start='2020-07-01', 
    end='2024-11-01', 
    freq='12M'
).tz_localize('UTC')  # Make cohort periods timezone-aware

# Dictionary to store tokens by cohort
cohort_tokens = {i: [] for i in range(len(cohort_periods)-1)}

# Assign tokens to cohorts based on their first appearance
for token, df in token_dfs.items():
    first_appearance = df['timestamp'].min()
    for i in range(len(cohort_periods)-1):
        if cohort_periods[i] <= first_appearance < cohort_periods[i+1]:
            cohort_tokens[i].append(token)
            break

# Create single plot
fig, ax1 = plt.subplots(figsize=(12, 8))

# Plot individual token market caps with dashed lines
for token, df in token_dfs.items():
    ax1.plot(df['timestamp'], df['marketCap']/1e9, label=token, alpha=0.3, linewidth=1, linestyle='--')

# Calculate and plot cohort averages
colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown']
for i, tokens in cohort_tokens.items():
    if tokens:  # Only process cohorts with tokens
        # Create a common date range for the cohort
        all_cohort_data = []
        
        for token in tokens:
            df = token_dfs[token].copy()
            # Resample to daily frequency and forward fill for up to 7 days
            df.set_index('timestamp', inplace=True)
            daily_data = df['marketCap'].resample('D').ffill(limit=7)
            all_cohort_data.append(daily_data)
        
        # Combine all token data for the cohort
        if all_cohort_data:
            # Align all series and calculate mean
            cohort_data = pd.concat(all_cohort_data, axis=1)
            cohort_mean = cohort_data.mean(axis=1)
            
            # Remove any remaining NaN values
            cohort_mean = cohort_mean.dropna()
            
            if not cohort_mean.empty:
                period_start = cohort_periods[i].strftime('%Y-%m')
                period_end = cohort_periods[i+1].strftime('%Y-%m')
                
                ax1.plot(cohort_mean.index, cohort_mean.values/1e9,
                        label=f'Avg {period_start} to {period_end}',
                        color=colors[i % len(colors)],
                        linewidth=2)

# Adjust the y-axis to scale with individual coins and cohorts
all_market_caps = [df['marketCap'].max() for df in token_dfs.values()]
all_cohort_means = [max(cohort_mean) for i, tokens in cohort_tokens.items() if tokens for token in tokens if token in token_dfs]
max_market_cap = max(all_market_caps + all_cohort_means)
ax1.set_ylim(bottom=0)  # Ensure the y-axis starts at 0
ax1.set_ylim(top=max_market_cap * 1.1)  # Add 10% headroom

# # Get total gaming market cap data from API
# url = "https://api.coinmarketcap.com/data-api/v3/sector/w/market-chart"
# params = {
#     'tagSlug': 'gaming',
#     'range': 'all'
# }

# try:
#     response = requests.get(url, params=params)
#     response.raise_for_status()
#     data = response.json()
    
#     if 'data' in data and 'marketCapPoints' in data['data']:
#         points = data['data']['marketCapPoints']
#         gaming_df = pd.DataFrame(points)
#         gaming_df['timestamp'] = pd.to_datetime(gaming_df['timestamp'].astype(float), unit='ms')
#         if 'value' in gaming_df.columns:
#             gaming_df = gaming_df.rename(columns={'value': 'marketCap'})
#         gaming_df['marketCap'] = gaming_df['marketCap'] / 1e9
        
#         # Commented out the total gaming market cap plot
#         # ax2 = ax1.twinx()
#         # ax2.plot(gaming_df['timestamp'], gaming_df['marketCap'],
#         #         label='Total Gaming Market Cap', color='black', linewidth=2)
#         # ax2.set_ylabel('Gaming Market Cap (Billions USD)')
#         # ax2.grid(False)  # Disable grid for the second y-axis

# except Exception as e:
#     print(f"Error getting gaming market cap data: {e}")

# Get Bitcoin market cap data from API

'''

bitcoin_url = "https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart"
bitcoin_params = {
    'id': '1',  # Bitcoin's ID
    'range': 'all'
}

try:
    bitcoin_response = requests.get(bitcoin_url, params=bitcoin_params)
    bitcoin_response.raise_for_status()
    bitcoin_data = bitcoin_response.json()
    print("Bitcoin Data:")
    print(bitcoin_data)
    
    if 'data' in bitcoin_data and 'points' in bitcoin_data['data']:
        bitcoin_points = bitcoin_data['data']['points']
        bitcoin_df = pd.DataFrame.from_dict(bitcoin_points, orient='index')
        bitcoin_df['timestamp'] = pd.to_datetime(bitcoin_df.index.astype(float), unit='s')  # Corrected to 's'
        if 'v' in bitcoin_df.columns:
            bitcoin_df = bitcoin_df.rename(columns={'v': 'marketCap'})
            bitcoin_df['marketCap'] = bitcoin_df['marketCap'].apply(lambda x: x if isinstance(x, (int, float)) else (x[0] if isinstance(x, list) and len(x) > 0 else None))  # Correct extraction
        bitcoin_df['marketCap'] = pd.to_numeric(bitcoin_df['marketCap'], errors='coerce') / 1e9  # Ensure numeric conversion
        
        # Filter data to start from 2020-07-01
        bitcoin_df = bitcoin_df[bitcoin_df['timestamp'] >= '2020-07-01']
        
        # Plot Bitcoin market cap on a new y-axis
        ax3 = ax1.twinx()
        ax3.plot(bitcoin_df['timestamp'], bitcoin_df['marketCap'],
                label='Bitcoin Market Cap', color='orange', linewidth=2)
        ax3.set_ylabel('Bitcoin Market Cap (Billions USD)')
        ax3.grid(False)  # Disable grid for the third y-axis

except Exception as e:
    print(f"Error getting Bitcoin market cap data: {e}")

'''

# Customize the plot
ax1.set_title('Market Cap History Comparison')
ax1.set_xlabel('Date')
ax1.set_ylabel('Market Cap (Billions USD)')
ax1.grid(True)

# Add legend
ax1.legend(loc='upper left')
# ax2.legend(loc='upper right')  # Commented out the legend for the total gaming market cap
# ax3.legend(loc='upper right')

# Rotate x-axis labels and format dates
plt.xticks(rotation=45)
ax1.xaxis.set_major_formatter(DateFormatter('%m/%d/%y'))

# Limit x-axis to data points after 2020-07-01
# ax1.set_xlim(pd.to_datetime('2020-07-01'), bitcoin_df['timestamp'].max())

# Adjust layout
plt.tight_layout()

# Display the plot
plt.show()