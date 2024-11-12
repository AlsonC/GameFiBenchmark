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

# print(filtered_df)
# print(df)

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
        else:
            print(f"No valid market cap data for {token}")
    except FileNotFoundError:
        print(f"Warning: No data file found for {token}")
    except Exception as e:
        print(f"Error processing {token}: {str(e)}")

# Add a check to ensure we have data
if not token_dfs:
    raise ValueError("No data was loaded successfully. Please check the CSV files and their formats.")


print(df)
print(token_dfs)
# Create cohort periods (12-month intervals) with UTC timezone
cohort_periods = pd.date_range(
    start='2020-07-01', 
    end='2024-11-01', 
    freq='12ME'
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
    if not df.empty:
        ax1.plot(df['timestamp'], df['marketCap'], label=token, alpha=0.3, linewidth=1, linestyle='--')
    else:
        print(f"Token {token} has no data to plot.")

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
                # print(cohort_mean)
                period_start = cohort_periods[i].strftime('%Y-%m')
                period_end = cohort_periods[i+1].strftime('%Y-%m')
                
                ax1.plot(cohort_mean.index, cohort_mean.values,
                        label=f'Avg {period_start} to {period_end}',
                        color=colors[i % len(colors)],
                        linewidth=2)
            else:
                print(f"Cohort {i} ({period_start} to {period_end}) has no valid data to plot.")

# Adjust the y-axis to scale with individual coins and cohorts
all_market_caps = [df['marketCap'].max() for df in token_dfs.values() if not df.empty]
all_cohort_means = [max(cohort_mean) for i, tokens in cohort_tokens.items() if tokens for token in tokens if token in token_dfs and not token_dfs[token].empty]
max_market_cap = max(all_market_caps + all_cohort_means, default=0)
ax1.set_ylim(bottom=0)  # Ensure the y-axis starts at 0
ax1.set_ylim(top=max_market_cap * 1.1 if max_market_cap > 0 else 1)  # Add 10% headroom or set a default

# Print diagnostic information
print("Max market cap values for individual tokens:", all_market_caps)
print("Max cohort mean values:", all_cohort_means)
print("Overall max market cap for scaling:", max_market_cap)

# Customize the plot
ax1.set_title('Market Cap History Comparison')
ax1.set_xlabel('Date')
ax1.set_ylabel('Market Cap (Billions USD)')
ax1.grid(True)

# Add legend
ax1.legend(loc='upper left')

# Rotate x-axis labels and format dates
plt.xticks(rotation=45)
ax1.xaxis.set_major_formatter(DateFormatter('%m/%d/%y'))

# Adjust layout
plt.tight_layout()

# Display the plot
plt.show()