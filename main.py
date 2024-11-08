import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from dotenv import load_dotenv
from binance.client import Client
from datetime import datetime

# Load environment variables
load_dotenv()
API_KEY = os.getenv("BINANCE_API_KEY")
SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Initialize Binance client
client = Client(API_KEY, SECRET_KEY)

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Complex Crypto Trading Dashboard"

# Layout for Fullscreen Display with Multiple Indicators
app.layout = html.Div(
    style={
        "backgroundColor": "#1e1e1e",
        "color": "#ffffff",
        "height": "100vh",
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
    },
    children=[
        html.H1("BTC/USDT Complex Trading Dashboard", style={"color": "#F5A623", "text-align": "center"}),

        # Real-time price chart with technical indicators
        dcc.Graph(id="live-price-graph", config={"displayModeBar": False}, style={"width": "95%", "height": "70%"}),

        # RSI indicator chart
        dcc.Graph(id="rsi-chart", config={"displayModeBar": False}, style={"width": "95%", "height": "20%"}),

        # Update interval every second
        dcc.Interval(id="graph-update", interval=1 * 1000),  # Update every 1 second
    ]
)

# Function to fetch historical data and compute indicators
def fetch_price_data():
    klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "1 hour ago UTC")
    df = pd.DataFrame(
        klines, columns=["time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base", "taker_buy_quote", "ignore"]
    )
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)
    df["close"] = df["close"].astype(float)
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["volume"] = df["volume"].astype(float)

    # Calculate moving averages
    df["MA_20"] = df["close"].rolling(window=20).mean()
    df["MA_55"] = df["close"].rolling(window=55).mean()
    df["MA_100"] = df["close"].rolling(window=100).mean()

    # Calculate Bollinger Bands
    df["BB_upper"] = df["MA_20"] + 2 * df["close"].rolling(window=20).std()
    df["BB_lower"] = df["MA_20"] - 2 * df["close"].rolling(window=20).std()

    # Calculate RSI
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df

# Callback for updating the graph and indicators
@app.callback(
    [Output("live-price-graph", "figure"),
     Output("rsi-chart", "figure")],
    [Input("graph-update", "n_intervals")]
)
def update_graph(n):
    # Fetch and process data
    df = fetch_price_data()

    # Create main candlestick chart with moving averages and Bollinger Bands
    fig = go.Figure(data=[
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="BTC/USDT",
            increasing_line_color="#00ff00",
            decreasing_line_color="#ff3333"
        ),
        go.Scatter(
            x=df.index, y=df["MA_20"],
            mode="lines", name="MA (20)", line=dict(color="#FF00FF", width=1.5)
        ),
        go.Scatter(
            x=df.index, y=df["MA_55"],
            mode="lines", name="MA (55)", line=dict(color="#0000FF", width=1.5)
        ),
        go.Scatter(
            x=df.index, y=df["MA_100"],
            mode="lines", name="MA (100)", line=dict(color="#FFAA00", width=1.5)
        ),
        go.Scatter(
            x=df.index, y=df["BB_upper"],
            mode="lines", name="Bollinger Upper", line=dict(color="#FFA500", width=1, dash="dash")
        ),
        go.Scatter(
            x=df.index, y=df["BB_lower"],
            mode="lines", name="Bollinger Lower", line=dict(color="#FFA500", width=1, dash="dash")
        ),
        go.Bar(
            x=df.index, y=df["volume"],
            name="Volume", marker_color="#666666", opacity=0.3, yaxis="y2"
        )
    ])
    fig.update_layout(
        title="BTC/USDT Live Price with Indicators",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        font=dict(color="#ffffff"),
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="#1e1e1e",
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right",
            showgrid=False
        )
    )

    # Create RSI chart
    rsi_fig = go.Figure(data=[
        go.Scatter(
            x=df.index, y=df["RSI"],
            mode="lines", name="RSI", line=dict(color="#FFFF00", width=1.5)
        )
    ])
    rsi_fig.update_layout(
        title="Relative Strength Index (RSI)",
        xaxis_title="Time",
        yaxis_title="RSI",
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        font=dict(color="#ffffff"),
        paper_bgcolor="#1e1e1e",
        plot_bgcolor="#1e1e1e",
        yaxis=dict(range=[0, 100]),
        shapes=[
            # Add RSI threshold lines at 30 and 70
            dict(type="line", x0=df.index.min(), x1=df.index.max(), y0=70, y1=70, line=dict(color="#FF0000", width=1, dash="dash")),
            dict(type="line", x0=df.index.min(), x1=df.index.max(), y0=30, y1=30, line=dict(color="#00FF00", width=1, dash="dash")),
        ]
    )

    return fig, rsi_fig

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True) 
