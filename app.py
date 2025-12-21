import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Page Config
st.set_page_config(
    page_title="Web Scraping Dashboard - 2023 Data",
    page_icon="📊",
    layout="wide"
)

# Load Data
@st.cache_data
def load_data():
    """Load scraped data from JSON file"""
    if not os.path.exists('data.json'):
        st.error("⚠️ data.json not found! Please run scraper_complete.py first.")
        st.info("Run: `python scraper_complete.py` to generate data")
        return None, None, None
    
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load each section separately
        reviews_df = pd.DataFrame(data.get('reviews', []))
        products_df = pd.DataFrame(data.get('products', []))
        testimonials_df = pd.DataFrame(data.get('testimonials', []))
        
        # Convert dates for reviews
        if not reviews_df.empty and 'date' in reviews_df.columns:
            reviews_df['date'] = pd.to_datetime(reviews_df['date'], errors='coerce')
        
        return reviews_df, products_df, testimonials_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

reviews_df, products_df, testimonials_df = load_data()

# --- Sidebar Navigation ---
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Select Section:", ["Reviews", "Products", "Testimonials"])

# --- PRODUCTS SECTION ---
if page == "Products":
    st.title("📦 Products Section")
    st.markdown("---")
    
    if products_df is not None and not products_df.empty:
        st.subheader(f"Total Products: {len(products_df)}")
        
        # Display products in a nice format
        for idx, product in products_df.iterrows():
            with st.expander(f"**{product.get('name', 'Unknown Product')}** - {product.get('price', 'N/A')}"):
                st.markdown(f"**Product ID:** {product.get('id', 'N/A')}")
                st.markdown(f"**Price:** {product.get('price', 'N/A')}")
                st.markdown(f"**Description:**")
                st.write(product.get('description', 'No description available'))
        
        # Display as dataframe
        st.markdown("---")
        st.subheader("📋 Products Table")
        display_df = products_df[['name', 'price', 'description']].copy()
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Statistics
        st.markdown("---")
        st.subheader("📊 Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Products", len(products_df))
        
        with col2:
            # Count products by price range
            if 'price' in products_df.columns:
                try:
                    products_df['price_num'] = products_df['price'].str.replace('$', '').astype(float)
                    avg_price = products_df['price_num'].mean()
                    st.metric("Average Price", f"${avg_price:.2f}")
                except:
                    st.metric("Average Price", "N/A")
    else:
        st.warning("⚠️ No product data loaded. Please run `python scraper_complete.py` first.")

# --- TESTIMONIALS SECTION ---
elif page == "Testimonials":
    st.title("💬 Testimonials Section")
    st.markdown("---")
    
    if testimonials_df is not None and not testimonials_df.empty:
        st.subheader(f"Total Testimonials: {len(testimonials_df)}")
        
        # Display testimonials in cards
        for idx, testimonial in testimonials_df.iterrows():
            rating = testimonial.get('rating', 0)
            stars = '⭐' * rating
            
            with st.container():
                st.markdown(f"### {stars}")
                st.write(f'"{testimonial.get("text", "")}"')
                st.markdown("---")
        
        # Display as dataframe
        st.subheader("📋 Testimonials Table")
        display_df = testimonials_df[['text', 'rating']].copy()
        display_df['rating'] = display_df['rating'].apply(lambda x: '⭐' * x)
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Statistics
        st.markdown("---")
        st.subheader("📊 Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Testimonials", len(testimonials_df))
        
        with col2:
            if 'rating' in testimonials_df.columns:
                avg_rating = testimonials_df['rating'].mean()
                st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
        
        with col3:
            if 'rating' in testimonials_df.columns:
                five_star_count = len(testimonials_df[testimonials_df['rating'] == 5])
                st.metric("5-Star Reviews", five_star_count)
        
        # Rating distribution chart
        if 'rating' in testimonials_df.columns:
            st.markdown("---")
            st.subheader("📊 Rating Distribution")
            
            rating_counts = testimonials_df['rating'].value_counts().sort_index()
            fig = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                labels={'x': 'Rating (Stars)', 'y': 'Count'},
                title='Testimonial Rating Distribution',
                color=rating_counts.values,
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No testimonial data loaded. Please run `python scraper_complete.py` first.")

# --- REVIEWS SECTION (Core Feature with Month Filter) ---
elif page == "Reviews":
    st.title("📊 2023 Reviews Analysis Dashboard")
    st.markdown("---")
    
    if reviews_df is None or reviews_df.empty:
        st.error("⚠️ No review data available. Please run `python scraper_complete.py` to collect reviews.")
        st.stop()
    
    # Month Selection
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📅 Filter Options")
    selected_month_name = st.sidebar.select_slider("Select Month (2023)", options=months, value="Jan")
    month_idx = months.index(selected_month_name) + 1
    
    # Filter Data by Month
    filtered_df = reviews_df[
        (reviews_df['date'].dt.month == month_idx) & 
        (reviews_df['date'].dt.year == 2023)
    ].copy()
    
    if not filtered_df.empty:
        # Key Metrics
        st.subheader(f"📈 Analytics for {selected_month_name} 2023")
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        total_reviews = len(filtered_df)
        avg_rating = filtered_df['rating'].mean()
        five_star = len(filtered_df[filtered_df['rating'] == 5])
        one_star = len(filtered_df[filtered_df['rating'] == 1])
        
        with col_m1:
            st.metric("Total Reviews", total_reviews)
        
        with col_m2:
            st.metric("Average Rating", f"{avg_rating:.2f} ⭐")
        
        with col_m3:
            st.metric("5-Star Reviews", five_star, delta=f"{five_star/total_reviews*100:.1f}%")
        
        with col_m4:
            st.metric("1-Star Reviews", one_star, delta=f"-{one_star/total_reviews*100:.1f}%", delta_color="inverse")
        
        st.markdown("---")
        
        # Display Reviews Table
        st.subheader(f"📋 Reviews for {selected_month_name} 2023")
        display_df = filtered_df[['date', 'title', 'text', 'rating']].copy()
        display_df['date'] = display_df['date'].dt.strftime("%Y-%m-%d")
        display_df['rating'] = display_df['rating'].apply(lambda x: '⭐' * x)
        st.dataframe(display_df, use_container_width=True, height=400)
        
        st.markdown("---")
        
        # Rating Distribution Chart
        st.subheader("📊 Rating Distribution")
        
        rating_counts = filtered_df['rating'].value_counts().sort_index()
        
        fig = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            labels={'x': 'Rating (Stars)', 'y': 'Number of Reviews'},
            title=f"Review Ratings Distribution - {selected_month_name} 2023",
            color=rating_counts.index,
            color_continuous_scale=['#e74c3c', '#f39c12', '#f1c40f', '#2ecc71', '#27ae60'],
            text=rating_counts.values
        )
        
        fig.update_traces(textposition='outside')
        fig.update_layout(
            xaxis_title="Rating (Stars)",
            yaxis_title="Number of Reviews",
            showlegend=False,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Word Cloud
        st.subheader(f"☁️ Word Cloud - {selected_month_name} 2023")
        
        all_text = " ".join(filtered_df['text'].astype(str))
        
        if all_text.strip():
            try:
                wordcloud = WordCloud(
                    width=1200,
                    height=600,
                    background_color='white',
                    colormap='viridis',
                    max_words=100,
                    relative_scaling=0.5,
                    min_font_size=10
                ).generate(all_text)
                
                fig, ax = plt.subplots(figsize=(15, 8))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                plt.close()
                
                st.caption(f"Word cloud generated from {total_reviews} reviews in {selected_month_name} 2023")
            except Exception as e:
                st.error(f"Error generating word cloud: {e}")
        else:
            st.info("No text available to generate word cloud")
        
        # Sentiment Analysis (if available)
        if 'sentiment' in filtered_df.columns and 'confidence' in filtered_df.columns:
            st.markdown("---")
            st.subheader("💭 Sentiment Analysis")
            
            # Calculate sentiment counts and average confidence
            positive_reviews = filtered_df[filtered_df['sentiment'] == 'POSITIVE']
            negative_reviews = filtered_df[filtered_df['sentiment'] == 'NEGATIVE']
            
            positive_count = len(positive_reviews)
            negative_count = len(negative_reviews)
            
            avg_confidence_positive = positive_reviews['confidence'].mean() if positive_count > 0 else 0
            avg_confidence_negative = negative_reviews['confidence'].mean() if negative_count > 0 else 0
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("✅ Positive", positive_count, delta=f"{positive_count/total_reviews*100:.1f}%")
            
            with col2:
                st.metric("❌ Negative", negative_count, delta=f"{negative_count/total_reviews*100:.1f}%")
            
            with col3:
                overall_avg_confidence = filtered_df['confidence'].mean()
                st.metric("Avg Confidence", f"{overall_avg_confidence:.1%}")
            
            # Bar Chart: Positive vs Negative with Average Confidence
            st.markdown("---")
            st.subheader("📊 Sentiment Distribution with Confidence Scores")
            
            sentiment_data = pd.DataFrame({
                'Sentiment': ['Positive', 'Negative'],
                'Count': [positive_count, negative_count],
                'Avg Confidence': [avg_confidence_positive, avg_confidence_negative]
            })
            
            # Create bar chart with confidence scores
            fig_sentiment = px.bar(
                sentiment_data,
                x='Sentiment',
                y='Count',
                title=f'Positive vs Negative Reviews - {selected_month_name} 2023',
                color='Sentiment',
                color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c'},
                text='Count',
                hover_data={
                    'Count': True,
                    'Avg Confidence': ':.2%',
                    'Sentiment': False
                }
            )
            
            # Add average confidence as annotation
            fig_sentiment.update_traces(
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<br>Avg Confidence: %{customdata[0]:.2%}<extra></extra>'
            )
            
            # Add annotations for confidence scores
            annotations = []
            for i, row in sentiment_data.iterrows():
                annotations.append(
                    dict(
                        x=row['Sentiment'],
                        y=row['Count'],
                        text=f"Confidence: {row['Avg Confidence']:.1%}",
                        showarrow=False,
                        yshift=20,
                        font=dict(size=11, color='gray')
                    )
                )
            
            fig_sentiment.update_layout(
                xaxis_title="Sentiment",
                yaxis_title="Number of Reviews",
                showlegend=False,
                height=500,
                annotations=annotations
            )
            
            st.plotly_chart(fig_sentiment, use_container_width=True)
    else:
        st.warning(f"⚠️ No reviews found for {selected_month_name} 2023")
        st.info("Try selecting a different month using the slider in the sidebar.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "This dashboard displays scraped data from web-scraping.dev including:\n"
    "- **Reviews**: 2023 product reviews with month filtering\n"
    "- **Products**: Product catalog with descriptions\n"
    "- **Testimonials**: User testimonials with ratings"
)
