import streamlit as st
import yfinance as yf
import mplfinance as mpf
import pandas as pd
from textblob import TextBlob

# ---------------- PAGE ----------------
st.set_page_config(page_title="MarketSense AI", layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("🛡️ MarketSense AI")
role = st.sidebar.selectbox("Select Role", ["Retail Investor", "Analyst", "Institutional"])
st.sidebar.success(f"Logged in as: {role}")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    try:
        df = yf.download("^NSEI", period="5y", interval="1d", auto_adjust=True, threads=False)

        # FIX: empty data fallback
        if df is None or df.empty:
            return None

        # FIX: multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[['Open','High','Low','Close','Volume']]
        df.dropna(inplace=True)

        return df

    except Exception as e:
        return None

df = load_data()

# ---------------- HARD SAFETY ----------------
if df is None or df.empty:
    st.error("❌ Market data not available (Yahoo Finance issue). Try again later.")
    st.stop()

# ---------------- CURRENT PRICE SAFE ----------------
try:
    close_series = df['Close'].dropna()

    if close_series.empty:
        st.error("❌ No closing price data available")
        st.stop()

    current_price = float(close_series.iloc[-1])

except Exception:
    st.error("❌ Error calculating current price")
    st.stop()

# ---------------- SENTIMENT ----------------
headlines = [
    "Market shows resilience",
    "NIFTY hits new high",
    "Global rally continues"
]

sentiment_score = sum(TextBlob(h).sentiment.polarity for h in headlines) / len(headlines)
sentiment_label = "Positive" if sentiment_score > 0 else "Negative"

# ---------------- UI ----------------
st.title("📈 NIFTY 50 Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("NIFTY 50", f"{current_price:.2f}")

prediction = current_price * 1.005
col2.metric("Prediction", f"{prediction:.2f}", "+0.5%")

col3.metric("Sentiment", sentiment_label, f"{sentiment_score:.2f}")

# ---------------- CHART ----------------
def plot_chart(data, title):
    try:
        if data is None or data.empty:
            st.warning(f"No data for {title}")
            return

        data = data[['Open','High','Low','Close','Volume']].dropna()

        if data.empty:
            st.warning(f"No valid OHLC data for {title}")
            return

        fig, _ = mpf.plot(
            data,
            type='candle',
            volume=True,
            style='charles',
            returnfig=True
        )
        st.pyplot(fig)

    except Exception as e:
        st.warning(f"Chart failed: {title}")

# ---------------- TABS ----------------
st.subheader("📊 Market Analysis")

tab1, tab2, tab3, tab4 = st.tabs(["Daily", "Monthly", "Quarterly", "Yearly"])

with tab1:
    plot_chart(df.tail(60), "Daily")

with tab2:
    plot_chart(df.resample('M').agg({
        'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'
    }), "Monthly")

with tab3:
    plot_chart(df.resample('Q').agg({
        'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'
    }), "Quarterly")

with tab4:
    plot_chart(df.resample('Y').agg({
        'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'
    }), "Yearly")

# ---------------- ALERT ----------------
st.subheader("🔔 Risk Monitor")

if sentiment_score > 0:
    st.success("Market Confidence: High")
else:
    st.warning("Volatility Warning")

st.divider()
st.caption("Powered by MarketSense AI | Data: Yahoo Finance")
