import streamlit as st
import yfinance as yf
import mplfinance as mpf
import pandas as pd
from textblob import TextBlob

st.set_page_config(page_title="MarketSense AI", layout="wide")

# Sidebar
st.sidebar.title("MarketSense AI")
role = st.sidebar.selectbox("Select Role", ["Retail Investor", "Analyst", "Institutional"])
st.sidebar.write(f"Logged in as: {role}")

# Load Data
@st.cache_data
def load_data():
    try:
        df = yf.download("^NSEI", period="5y", interval="1d", auto_adjust=True)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.error(e)
        return None

df = load_data()

if df is None or df.empty:
    st.error("❌ Data load failed")
    st.stop()

# Ensure columns
required_cols = ['Open','High','Low','Close','Volume']
if not all(col in df.columns for col in required_cols):
    st.error("❌ Data format issue")
    st.stop()

current_price = df['Close'].iloc[-1]

# Sentiment
headlines = ["Market shows resilience", "NIFTY hits new high", "Global rally"]
sentiment_score = sum(TextBlob(h).sentiment.polarity for h in headlines)/len(headlines)
sentiment_label = "Positive" if sentiment_score > 0 else "Negative"

# UI
st.title("📈 NIFTY 50 Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("NIFTY 50", f"{current_price:.2f}")
prediction = current_price * 1.005
col2.metric("Prediction", f"{prediction:.2f}", "+0.5%")
col3.metric("Sentiment", sentiment_label)

# Chart Function (FIXED)
def plot_chart(data):
    data = data[['Open','High','Low','Close','Volume']].dropna()
    fig, _ = mpf.plot(data, type='candle', returnfig=True, volume=True)
    st.pyplot(fig)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Daily","Monthly","Quarterly","Yearly"])

with tab1:
    plot_chart(df.tail(60))

with tab2:
    plot_chart(df.resample('M').agg({
        'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'
    }))

with tab3:
    plot_chart(df.resample('Q').agg({
        'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'
    }))

with tab4:
    plot_chart(df.resample('Y').agg({
        'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'
    }))
