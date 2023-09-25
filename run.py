import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
import calmap
from datetime import datetime, timedelta

def fetch_data(year):
    """
    Fetches the USD/BTC exchange rate data for a given year from the CoinGecko API using a rolling window of 90 days. 
    This circumvents the API's 90-day limit on historical hourly data.
    """
    end_date = datetime(year+1, 1, 1)  # Start of the next year
    start_date = end_date - timedelta(days=89)  # 90 days before the end_date
    all_data = []

    while start_date.year == year:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={start_date.timestamp()}&to={end_date.timestamp()}"
        response = requests.get(url)
        data = response.json()
        all_data.extend(data['prices'])
        end_date = start_date
        start_date = end_date - timedelta(days=90)

    df = pd.DataFrame(all_data, columns=['timestamp', 'price'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('date')
    df['high'] = df['price']
    df['low'] = df['price']
    df = df.resample('D').agg({'high': 'max', 'low': 'min'})
    df['spread'] = df['high'] - df['low']
    return df['spread']

def plot_calendar_heatmap(year):
    """
    Plots a calendar heatmap for the USD/BTC price spread for a given year.
    """
    data = fetch_data(year)
    vmin, vmax = data.min(), data.max()

    # Custom colormap from light orange to dark orange
    colors = ["#FFF6EB", "#FF4C00"]
    cmap = LinearSegmentedColormap.from_list("custom_orange", colors)
    
    # Plot the calendar heatmap
    colors = cmap(data)
    calmap.yearplot(data, year=year, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.title(f"USD/BTC Price Spread for {year}")
    plt.savefig(f"heatmap_{year}.png")
    plt.show()

if __name__ == "__main__":
 
    year = int(input("Enter the year (e.g. 2022): "))
    plot_calendar_heatmap(year)
