import streamlit as st
import pandas as pd
import json
import os
from transformers import pipeline
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="Brand Sentinel 2023 | Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Load Sentiment Model (Hugging Face)
@st.cache_resource
def load_model():
    """Load pre-trained sentiment analysis model from Hugging Face"""
    try:
        return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    except Exception as e:
        st.error(f"Failed to load sentiment model: {e}")
        return None

sentiment_pipeline = load_model()

# Load Data
@st.cache_data
def load_data():
    """Load scraped review data from JSON file"""
    if not os.path.exists('data.json'):
        st.error("⚠️ data.json not found! Please run scraper.py first.")
        st.info("Run: `python scraper.py` to generate data.json")
        return pd.DataFrame()
    
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# --- Sidebar Navigation ---
st.sidebar.markdown('<div class="main-header">🔍 Navigation</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")
page = st.sidebar.radio("Go to:", ["📊 Reviews (Analysis)", "📦 Products", "💬 Testimonials"], index=0)

# --- Products/Testimonials Sections ---
if page == "📦 Products":
    st.markdown('<div class="main-header">📦 Product Catalog</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if not df.empty:
        products_df = df[df['section'] == 'Products'] if 'section' in df.columns else pd.DataFrame()
        
        if not products_df.empty:
            st.dataframe(products_df, use_container_width=True)
        else:
            st.info("No products data available. This section shows product information if present in scraped data.")
    else:
        st.warning("No data loaded. Please run the scraper first.")

elif page == "💬 Testimonials":
    st.markdown('<div class="main-header">💬 Client Testimonials</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if not df.empty:
        testimonials_df = df[df['section'] == 'Testimonials'] if 'section' in df.columns else pd.DataFrame()
        
        if not testimonials_df.empty:
            st.table(testimonials_df)
        else:
            st.info("No testimonials data available. This section shows testimonial information if present in scraped data.")
    else:
        st.warning("No data loaded. Please run the scraper first.")

# --- Reviews (Core Feature) ---
elif page == "📊 Reviews (Analysis)":
    st.markdown('<div class="main-header">📊 2023 Sentiment Analysis Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    if df.empty:
        st.error("⚠️ No data available. Please run `python scraper.py` to collect reviews.")
        st.stop()
    
    if sentiment_pipeline is None:
        st.error("⚠️ Sentiment analysis model failed to load. Please check your internet connection and try again.")
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
        # Perform Sentiment Analysis
        with st.spinner("🤖 Analyzing sentiments with Hugging Face AI..."):
            try:
                # Process texts in batches for better performance
                texts = filtered_df['text'].tolist()
                results = sentiment_pipeline(texts, truncation=True, max_length=512)
                
                filtered_df['Sentiment'] = [res['label'] for res in results]
                filtered_df['Confidence'] = [round(res['score'], 4) for res in results]
                
                # Map POSITIVE/NEGATIVE to more readable format
                filtered_df['Sentiment_Display'] = filtered_df['Sentiment'].map({
                    'POSITIVE': '✅ Positive',
                    'NEGATIVE': '❌ Negative'
                })
                
            except Exception as e:
                st.error(f"Error during sentiment analysis: {e}")
                st.stop()
        
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
        st.subheader(f"📋 Detailed Reviews")
        display_df = filtered_df[['date', 'title', 'text', 'Sentiment_Display', 'Confidence']].copy()
        display_df['date'] = display_df['date'].dt.strftime("%Y-%m-%d")
        display_df = display_df.rename(columns={
            'date': 'Date',
            'title': 'Title',
            'text': 'Review Text',
            'Sentiment_Display': 'Sentiment',
            'Confidence': 'Confidence'
        })
        st.dataframe(display_df, use_container_width=True, height=300)
        
        st.markdown("---")
        
        # --- Visualization ---
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Sentiment Distribution")
            
            # Count plot with confidence overlay
            sentiment_counts = filtered_df['Sentiment'].value_counts().reset_index()
            sentiment_counts.columns = ['Sentiment', 'Count']
            
            # Calculate average confidence per sentiment
            avg_conf_by_sentiment = filtered_df.groupby('Sentiment')['Confidence'].mean().reset_index()
            sentiment_counts = sentiment_counts.merge(avg_conf_by_sentiment, on='Sentiment')
            
            # Create bar chart
            fig = px.bar(
                sentiment_counts,
                x='Sentiment',
                y='Count',
                color='Sentiment',
                title=f"Sentiment Distribution (Overall Confidence: {avg_confidence:.2%})",
                color_discrete_map={'POSITIVE': '#28a745', 'NEGATIVE': '#dc3545'},
                text='Count',
                hover_data={'Confidence': ':.2%'}
            )
            
            fig.update_traces(textposition='outside')
            fig.update_layout(
                xaxis_title="Sentiment",
                yaxis_title="Number of Reviews",
                showlegend=False,
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Additional confidence metrics
            st.markdown("**Confidence Metrics:**")
            for _, row in sentiment_counts.iterrows():
                st.write(f"- {row['Sentiment']}: {row['Confidence']:.2%} average confidence")
        
        with col2:
            # BONUS: Word Cloud
            st.subheader("☁️ Key Terms (Word Cloud)")
            
            try:
                text_combined = " ".join(filtered_df['text'].tolist())
                
                if len(text_combined.strip()) > 0:
                    wordcloud = WordCloud(
                        background_color="white",
                        width=800,
                        height=400,
                        colormap='viridis',
                        max_words=100,
                        relative_scaling=0.5,
                        min_font_size=10
                    ).generate(text_combined)
                    
                    fig_wc, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis("off")
                    ax.set_title(f"Most Frequent Terms - {selected_month_name} 2023", fontsize=14, pad=10)
                    st.pyplot(fig_wc)
                else:
                    st.warning("Not enough text data to generate word cloud.")
            except Exception as e:
                st.error(f"Error generating word cloud: {e}")
        
        st.markdown("---")
        
        # --- Additional Insights ---
        st.subheader("💡 Additional Insights")
        
        col_i1, col_i2 = st.columns(2)
        
        with col_i1:
            st.markdown("**Confidence Distribution:**")
            fig_conf = px.histogram(
                filtered_df,
                x='Confidence',
                nbins=20,
                color='Sentiment',
                title="Confidence Score Distribution",
                color_discrete_map={'POSITIVE': '#28a745', 'NEGATIVE': '#dc3545'}
            )
            fig_conf.update_layout(height=300)
            st.plotly_chart(fig_conf, use_container_width=True)
        
        with col_i2:
            st.markdown("**Daily Review Volume:**")
            daily_counts = filtered_df.groupby(filtered_df['date'].dt.day).size().reset_index()
            daily_counts.columns = ['Day', 'Count']
            
            fig_daily = px.line(
                daily_counts,
                x='Day',
                y='Count',
                title=f"Daily Review Count - {selected_month_name} 2023",
                markers=True
            )
            fig_daily.update_layout(height=300)
            st.plotly_chart(fig_daily, use_container_width=True)
            
    else:
        st.warning(f"⚠️ No reviews found for {selected_month_name} 2023. Try another month or run the scraper again.")
        
        # Show available data summary
        if not df.empty:
            st.info(f"**Total reviews in dataset:** {len(df)}")
            if 'date' in df.columns:
                date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
                st.info(f"**Date range:** {date_range}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**About:**")
st.sidebar.info(
    "This app uses Hugging Face's DistilBERT model for sentiment analysis. "
    "Reviews are scraped from web-scraping.dev and analyzed in real-time."
)