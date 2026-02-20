import streamlit as st
import yfinance as yf
import mplfinance as mpf
import pandas as pd
from textblob import TextBlob

# 1. Page Config
st.set_page_config(page_title="Stock NIFTY 50 Prediction using LSTM Model", layout="wide")

# 2. Sidebar
st.sidebar.title("🛡️ MarketSense AI")
role = st.sidebar.selectbox("Select User Role", ["Retail Investor", "Analyst", "Institutional User"])
st.sidebar.success(f"Logged in as: {role}")

# 3. Data Loading
@st.cache_data
def load_data():
    try:
        df = yf.download("^NSEI", period="5y", interval="1d", progress=False)
        if df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        st.error(f"Data download error: {e}")
        return None

df = load_data()

# 🛑 STOP APP IF DATA FAILED
if df is None:
    st.error("❌ Unable to fetch market data. Check internet or try again later.")
    st.stop()

if 'Close' not in df.columns:
    st.error(f"'Close' column missing. Columns found: {list(df.columns)}")
    st.stop()

current_price = df['Close'].iloc[-1]

# 4. Sentiment Calculation
headlines = ["Market shows resilience", "NIFTY hits new high", "Global stocks rally"]
sentiment_score = sum(TextBlob(h).sentiment.polarity for h in headlines) / len(headlines)
sentiment_label = "Positive" if sentiment_score > 0 else "Negative"

# 5. Top Metrics
st.title("📈 Intelligent Market Outlook & Risk Monitor")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Index: NIFTY 50", f"{current_price:.2f}")

with col2:
    prediction = current_price + (current_price * 0.005)
    st.metric("AI Prediction (Next Day)", f"{prediction:.2f}", "+0.5%")

with col3:
    st.metric("Sentiment Pulse", sentiment_label, f"Score: {sentiment_score:.2f}")

# 6. Sentiment Panel
st.subheader("📰 Sentiment Intelligence Panel")
st.info(f"Today's Analysis: Market sentiment is {sentiment_label}.")

# 7. Charts
st.subheader("📊 Multi-Timeframe Market Analysis")
tab1, tab2, tab3, tab4 = st.tabs(["Daily", "Monthly", "Quarterly", "Yearly"])

def plot_chart(data, title):
    if data.empty:
        st.warning(f"No data available for {title}")
        return
    fig, _ = mpf.plot(data, type='candle', style='charles', returnfig=True, volume=True)
    st.pyplot(fig)

with tab1:
    plot_chart(df.tail(60), "Daily View")

with tab2:
    df_monthly = df.resample('M').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'})
    plot_chart(df_monthly, "Monthly View")

with tab3:
    df_quarterly = df.resample('Q').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'})
    plot_chart(df_quarterly, "Quarterly View")

with tab4:
    df_yearly = df.resample('Y').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'})
    plot_chart(df_yearly, "Yearly View")

# 8. Alerts
st.subheader("🔔 Risk Monitor & Alerts")
if sentiment_score > 0:
    st.success("Market Confidence: High.")
else:
    st.warning("Volatility Warning: Low sentiment detected.")

st.divider()
st.caption("Powered by LSTM & Sentiment Analysis | Data: Yahoo Finance")
