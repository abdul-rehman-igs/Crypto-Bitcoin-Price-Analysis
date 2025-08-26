import requests
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

# ----------------------
# Fetch Crypto Data (Bitcoin)
# ----------------------
def fetch_crypto_data(symbol="bitcoin", currency="usd", days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency={currency}&days={days}"
    response = requests.get(url)
    data = response.json()

    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)

    # Add moving averages
    df["MA7"] = df["price"].rolling(window=7).mean()
    df["MA14"] = df["price"].rolling(window=14).mean()
    return df

# Initial Data Load
df = fetch_crypto_data()

# ----------------------
# Build Dashboard
# ----------------------
app = Dash(__name__)

app.layout = html.Div([
    html.H1("📊 Crypto Dashboard (Bitcoin)", style={"textAlign": "center"}),

    dcc.Dropdown(
        id="days-dropdown",
        options=[
            {"label": "7 Days", "value": 7},
            {"label": "30 Days", "value": 30},
            {"label": "90 Days", "value": 90},
        ],
        value=30,
        clearable=False
    ),

    dcc.Graph(id="price-chart"),
    dcc.Graph(id="volatility-chart")
])

# ----------------------
# Callbacks
# ----------------------
@app.callback(
    [Output("price-chart", "figure"),
     Output("volatility-chart", "figure")],
    [Input("days-dropdown", "value")]
)
def update_charts(days):
    df = fetch_crypto_data(days=days)

    # Price + Moving Averages
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(x=df.index, y=df["price"], mode="lines", name="Price"))
    price_fig.add_trace(go.Scatter(x=df.index, y=df["MA7"], mode="lines", name="7-day MA"))
    price_fig.add_trace(go.Scatter(x=df.index, y=df["MA14"], mode="lines", name="14-day MA"))
    price_fig.update_layout(title="Bitcoin Price & Moving Averages")

    # Volatility (daily % change)
    df["returns"] = df["price"].pct_change()
    volatility_fig = go.Figure()
    volatility_fig.add_trace(go.Bar(x=df.index, y=df["returns"] * 100, name="Daily % Change"))
    volatility_fig.update_layout(title="Bitcoin Daily Volatility (%)")

    return price_fig, volatility_fig

# ----------------------
# Run App
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)
