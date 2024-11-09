# Real-Time Crypto Dashboard

This repository contains a real-time cryptocurrency dashboard built with Python, Dash, and Plotly. It includes two primary Dash applications:

1. **Complex Crypto Trading Dashboard** - A dashboard featuring candlestick charts with multiple technical indicators for BTC/USDT.
2. **Multi-Chart Real-Time Line Dashboard** - A dashboard that displays real-time price line charts for multiple cryptocurrencies.

## Features

- Real-time price updates from Binance API for multiple cryptocurrency pairs.
- Candlestick charts with technical indicators: Moving Averages (MA), Bollinger Bands, and RSI for BTC/USDT.
- Multi-chart display for live prices of BTC, ETH, BNB, ADA, XRP, and SOL.
- Adjustable update intervals for live data refresh.

## Prerequisites

Ensure you have these installed:

- Python 3.8 or higher
- [Dash](https://dash.plotly.com/)
- [pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [python-binance](https://github.com/sammchardy/python-binance)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
