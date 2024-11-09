from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from graphs import bar_graph, line_graph

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"

# Get API key from .env file
def APIConfigure():
    load_dotenv()
    api_key = os.getenv("Alpha_API_Key")
    return api_key

# Get stock symbols from CSV
def get_stock_symbols():
    try:
        stock_data = pd.read_csv("stocks.csv")
    except:
        print("Error reading CSV")
        return []
    
    stock_symbols = stock_data['Symbol'].tolist()
    stock_symbols.sort()
    return stock_symbols

# Function to query Alpha Vantage API and return stock data
def stock_data(symbol: str, time_series: str, start_date: str, end_date: str) -> dict:
    api_key = APIConfigure()


    time_series_map = {
        "1": "TIME_SERIES_INTRADAY",
        "2": "TIME_SERIES_DAILY",
        "3": "TIME_SERIES_WEEKLY",
        "4": "TIME_SERIES_MONTHLY", 
    }


    parameters = {
        "function": time_series_map[time_series],
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "full"
    }

    if time_series == "1":
        parameters["interval"] = "5min"


    url = "https://www.alphavantage.co/query"


    r = requests.get(url, params=parameters)


    if r.status_code != 200:
        return {"error": "Error fetching data from API"}


    data = r.json()


    if "Error Message" in data:
        return {"error": data["Error Message"]}


    if time_series == "1":
        key = "Time Series (5min)"
    elif time_series == "2":
        key = "Time Series (Daily)"
    elif time_series == "3":
        key = "Weekly Time Series"
    elif time_series == "4":
        key = "Monthly Time Series"

    time_series_data = data.get(key, {})


    filtered_data_dic = {
        date: values for date, values in time_series_data.items() if start_date <= date.split(' ')[0] <= end_date
    }


    dates, opens, highs, lows, closes = [], [], [], [], []


    for date, values in sorted(filtered_data_dic.items()):
        dates.append(date.split(' ')[0])
        opens.append(float(values["1. open"]))
        highs.append(float(values["2. high"]))
        lows.append(float(values["3. low"]))
        closes.append(float(values["4. close"]))

    
    return {"dates": dates, "open": opens, "high": highs, "low": lows, "close": closes}

@app.route('/')
def index():
    stock_symbols = get_stock_symbols()
    return render_template('index.html', stock_symbols=stock_symbols)

@app.route('/stock-data', methods=['POST'])
def get_stock_data():

    symbol = request.form.get('stock-symbol')
    time_series = request.form.get('time-series')
    chart_type = request.form.get('chart-type')
    start_date = request.form.get('start-date')
    end_date = request.form.get('end-date')

    # error checking for form filled out
    if not symbol or not time_series or not chart_type or not start_date or not end_date:
        flash("Please fill in all fields.", "error")
        return redirect(url_for('index'))
    
    if start_date and end_date:
        if end_date < start_date:
            flash("End date cannot be before start date.")
            return redirect(url_for('index'))
        elif end_date > datetime.today().date().isoformat():
            flash("End date cannot be later than today's date.")
            return redirect(url_for('index'))


    data = stock_data(symbol, time_series, start_date, end_date)

    # check for errors in the API response
    if "error" in data:
        flash("There was an issue querying the API")
        return redirect(url_for('index'))

    # generate chart
    if chart_type == "bar":
        chart = bar_graph(f"{symbol} Stock Data", data["dates"], data["open"], data["high"], data["low"], data["close"])
    elif chart_type == "line":
        chart = line_graph(f"{symbol} Stock Data", data["dates"], data["open"], data["high"], data["low"], data["close"])

    return render_template('index.html', stock_symbols=get_stock_symbols(), chart=chart)

if __name__ == "__main__":
    app.run(debug=True)