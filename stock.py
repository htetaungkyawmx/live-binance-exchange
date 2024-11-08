import os
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dotenv import load_dotenv
from binance.client import Client
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Initialize Binance client
client = Client(API_KEY, SECRET_KEY)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Multi-Chart Real-Time Line Dashboard"

# Dictionary to hold data for each symbol to keep history over time
data_storage = {symbol: pd.DataFrame(columns=["time", "price"]) for symbol in ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT"]}

# Layout of the app
app.layout = html.Div(
    style={"backgroundColor": "#1e1e1e", "color": "#ffffff", "padding": "10px"},
    children=[
        html.H1("Real-Time Multi-Chart Line Dashboard", style={"text-align": "center", "color": "#F5A623"}),

        # Layout for multiple charts
        html.Div(
            style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "10px"},
            children=[
                dcc.Graph(id="chart-btc", config={"displayModeBar": False}),
                dcc.Graph(id="chart-eth", config={"displayModeBar": False}),
                dcc.Graph(id="chart-bnb", config={"displayModeBar": False}),
                dcc.Graph(id="chart-ada", config={"displayModeBar": False}),
                dcc.Graph(id="chart-xrp", config={"displayModeBar": False}),
                dcc.Graph(id="chart-sol", config={"displayModeBar": False}),
            ]
        ),
        
        # Interval component to update charts every second
        dcc.Interval(id="interval-component", interval=1 * 1000, n_intervals=0)
    ]
)

# Function to fetch the latest price for a given symbol
def fetch_latest_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    timestamp = datetime.now()
    price = float(ticker['price'])
    return timestamp, price

# Callback to update each chart with live data every second
@app.callback(
    [Output("chart-btc", "figure"), Output("chart-eth", "figure"), Output("chart-bnb", "figure"),
     Output("chart-ada", "figure"), Output("chart-xrp", "figure"), Output("chart-sol", "figure")],
    [Input("interval-component", "n_intervals")]
)
def update_charts(n):
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT", "SOLUSDT"]
    figures = []

    for symbol in symbols:
        # Fetch latest price and update data storage
        timestamp, price = fetch_latest_price(symbol)
        new_data = pd.DataFrame([[timestamp, price]], columns=["time", "price"])
        
        # Append new data, and keep only recent 60 data points for each symbol
        data_storage[symbol] = pd.concat([data_storage[symbol], new_data]).iloc[-60:]

        # Create line chart with Plotly
        fig = go.Figure(data=[
            go.Scatter(
                x=data_storage[symbol]["time"],
                y=data_storage[symbol]["price"],
                mode="lines",
                name=symbol
            )
        ])
        
        fig.update_layout(
            title=f"{symbol} Live Price",
            xaxis_title="Time",
            yaxis_title="Price (USDT)",
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            font=dict(color="#ffffff"),
            paper_bgcolor="#1e1e1e",
            plot_bgcolor="#1e1e1e",
        )
        
        figures.append(fig)

    return figures

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
