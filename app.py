import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="Brand Sentinel 2023 - Sentiment Analysis",
    page_icon="📊",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    """Load scraped review data with pre-computed sentiments from JSON file"""
    if not os.path.exists('data.json'):
        st.error("⚠️ data.json not found! Please run scraper.py first.")
        st.info("Run: `python scraper.py` to generate data.json with sentiment analysis")
        return pd.DataFrame()
    
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Verify sentiment data exists
        if 'sentiment' not in df.columns or 'confidence' not in df.columns:
            st.error("⚠️ Sentiment data missing! Please re-run scraper.py to compute sentiments.")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Section:", ["Reviews", "Products", "Testimonials"])

# --- Products/Testimonials Sections ---
if page == "Products":
    st.header("📦 Products")
    
    if not df.empty:
        products_df = df[df['section'] == 'Products'] if 'section' in df.columns else pd.DataFrame()
        
        if not products_df.empty:
            st.dataframe(products_df, use_container_width=True)
        else:
            st.info("No products data available in the dataset.")
    else:
        st.warning("No data loaded. Please run scraper.py first.")

elif page == "Testimonials":
    st.header("💬 Testimonials")
    
    if not df.empty:
        testimonials_df = df[df['section'] == 'Testimonials'] if 'section' in df.columns else pd.DataFrame()
        
        if not testimonials_df.empty:
            st.dataframe(testimonials_df, use_container_width=True)
        else:
            st.info("No testimonials data available in the dataset.")
    else:
        st.warning("No data loaded. Please run scraper.py first.")

# --- Reviews (Core Feature) ---
elif page == "Reviews":
    st.header("📊 2023 Sentiment Analysis Dashboard")
    
    if df.empty:
        st.error("⚠️ No data available. Please run `python scraper.py` to collect reviews.")
        st.stop()
    
    # Month Selection
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Filter Options")
    selected_month_name = st.sidebar.select_slider("Select Month (2023)", options=months, value="Jan")
    month_idx = months.index(selected_month_name) + 1
    
    # Filter Data
    filtered_df = df[(df['date'].dt.month == month_idx) & (df['date'].dt.year == 2023)].copy()
    
    if not filtered_df.empty:
        # Use pre-computed sentiment data
        filtered_df['Sentiment'] = filtered_df['sentiment']
        filtered_df['Confidence'] = filtered_df['confidence']
        
        # Map POSITIVE/NEGATIVE to more readable format
        filtered_df['Sentiment_Display'] = filtered_df['Sentiment'].map({
            'POSITIVE': '✅ Positive',
            'NEGATIVE': '❌ Negative'
        })
        
        # --- Key Metrics ---
        st.subheader(f"📈 Analytics for {selected_month_name} 2023")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        total_reviews = len(filtered_df)
        positive_count = (filtered_df['Sentiment'] == 'POSITIVE').sum()
        negative_count = (filtered_df['Sentiment'] == 'NEGATIVE').sum()
        avg_confidence = filtered_df['Confidence'].mean()
        
        with col_m1:
            st.metric("Total Reviews", total_reviews)
        
        with col_m2:
            st.metric("✅ Positive", positive_count, delta=f"{positive_count/total_reviews*100:.1f}%")
        
        with col_m3:
            st.metric("❌ Negative", negative_count, delta=f"{negative_count/total_reviews*100:.1f}%")
        
        with col_m4:
            st.metric("Avg Confidence", f"{avg_confidence:.2%}")
        
        st.markdown("---")
        
        # Display Table
        st.subheader(f"📋 Reviews for {selected_month_name} 2023")
        display_df = filtered_df[['date', 'title', 'text', 'Sentiment', 'Confidence']].copy()
        display_df['date'] = display_df['date'].dt.strftime("%Y-%m-%d")
        st.dataframe(display_df, use_container_width=True)
        
        st.markdown("---")
        
        # --- Visualization: Bar Chart (Required) ---
        st.subheader("📊 Sentiment Distribution")
        
        # Calculate sentiment counts and average confidence
        sentiment_counts = filtered_df['Sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        
        # Calculate average confidence per sentiment
        avg_conf_by_sentiment = filtered_df.groupby('Sentiment')['Confidence'].mean().reset_index()
        sentiment_counts = sentiment_counts.merge(avg_conf_by_sentiment, on='Sentiment')
        
        # Create bar chart with confidence scores
        fig = px.bar(
            sentiment_counts,
            x='Sentiment',
            y='Count',
            color='Sentiment',
            title=f"Positive vs Negative Reviews - {selected_month_name} 2023<br><sub>Overall Average Confidence: {avg_confidence:.1%}</sub>",
            color_discrete_map={'POSITIVE': '#2ecc71', 'NEGATIVE': '#e74c3c'},
            text='Count',
            hover_data={'Confidence': ':.1%'},
            labels={'Count': 'Number of Reviews', 'Confidence': 'Avg Confidence'}
        )
        
        fig.update_traces(
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<br>Avg Confidence: %{customdata[0]:.1%}<extra></extra>'
        )
        
        fig.update_layout(
            xaxis_title="Sentiment",
            yaxis_title="Number of Reviews",
            showlegend=False,
            height=500,
            font=dict(size=14)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show detailed confidence metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Positive Reviews Avg Confidence", 
                     f"{sentiment_counts[sentiment_counts['Sentiment']=='POSITIVE']['Confidence'].values[0]:.1%}" 
                     if 'POSITIVE' in sentiment_counts['Sentiment'].values else "N/A")
        with col2:
            st.metric("Negative Reviews Avg Confidence", 
                     f"{sentiment_counts[sentiment_counts['Sentiment']=='NEGATIVE']['Confidence'].values[0]:.1%}" 
                     if 'NEGATIVE' in sentiment_counts['Sentiment'].values else "N/A")
            
    else:
        st.warning(f"⚠️ No reviews found for {selected_month_name} 2023. Try another month.")
        
        # Show available data summary
        if not df.empty:
            st.info(f"Total reviews in dataset: {len(df)}")
            if 'date' in df.columns:
                date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
                st.info(f"Date range: {date_range}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "**Sentiment Analysis**\n\n"
    "Model: DistilBERT (Hugging Face)\n\n"
    "Sentiments pre-computed during scraping\n\n"
    "Data: web-scraping.dev"
)