import requests
import json
from datetime import datetime
import time
from transformers import pipeline

# Load sentiment model once at module level
print("🤖 Loading Hugging Face sentiment model...")
try:
    sentiment_pipeline = pipeline("sentiment-analysis", 
                                 model="distilbert-base-uncased-finetuned-sst-2-english",
                                 device=-1)  # CPU
    print("✅ Model loaded successfully!\n")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    sentiment_pipeline = None

def scrape_data():
    """
    Scrapes review data from web-scraping.dev using GraphQL API.
    Fetches ALL reviews and filters for year 2023 to simulate real brand monitoring.
    """
    print("🌐 Starting web scraping from https://web-scraping.dev/reviews...")
    print("🎯 Target: All reviews from year 2023")
    print("=" * 70)
    
    graphql_url = "https://web-scraping.dev/api/graphql"
    all_reviews = []
    
    # GraphQL query for fetching reviews
    query_template = """
    query GetReviews($first: Int, $after: String) {
        reviews(first: $first, after: $after) {
            edges {
                node {
                    rid
                    text
                    rating
                    date
                }
                cursor
            }
            pageInfo {
                endCursor
                hasNextPage
            }
        }
    }
    """
    
    try:
        page_num = 1
        has_next_page = True
        cursor = None
        batch_size = 50  # Fetch 50 reviews per request
        max_pages = 20  # Fetch up to 20 pages to ensure we get full 2023 coverage
        
        while has_next_page and page_num <= max_pages:
            print(f"\n📄 Fetching page {page_num}...")
            
            # Prepare GraphQL request
            variables = {"first": batch_size}
            if cursor:
                variables["after"] = cursor
            
            payload = {
                "query": query_template,
                "variables": variables
            }
            
            # Make API request
            response = requests.post(graphql_url, json=payload, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for errors
            if "errors" in data:
                print(f"❌ GraphQL Error: {data['errors']}")
                break
            
            # Extract reviews
            edges = data.get("data", {}).get("reviews", {}).get("edges", [])
            page_info = data.get("data", {}).get("reviews", {}).get("pageInfo", {})
            
            if not edges:
                print("ℹ️  No more reviews found.")
                break
            
            # Process each review
            for edge in edges:
                node = edge.get("node", {})
                
                review_id = node.get("rid", "unknown")
                text = node.get("text", "")
                rating = node.get("rating", 0)
                date_str = node.get("date", "")
                
                # Parse date into proper format
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    
                    # Filter: Only include reviews from 2023
                    if date_obj.year != 2023:
                        continue
                        
                except ValueError:
                    # Skip reviews with invalid dates
                    continue
                
                # Create title from review ID (e.g., "red-potion-4" -> "Red Potion Review")
                title = " ".join(word.capitalize() for word in review_id.rsplit('-', 1)[0].split('-'))
                title = f"{title} Review"
                
                # Pre-compute sentiment analysis
                sentiment_label = "UNKNOWN"
                sentiment_score = 0.0
                
                if sentiment_pipeline and text:
                    try:
                        result = sentiment_pipeline(text[:512], truncation=True)[0]
                        sentiment_label = result['label']
                        sentiment_score = round(result['score'], 4)
                    except Exception as e:
                        print(f"   ⚠️  Sentiment analysis failed for review {review_id}: {e}")
                
                all_reviews.append({
                    "id": review_id,
                    "title": title,
                    "text": text,
                    "rating": rating,
                    "date": formatted_date,
                    "section": "Reviews",
                    "sentiment": sentiment_label,
                    "confidence": sentiment_score
                })
            
            print(f"   ✅ Fetched {len(edges)} reviews from page (2023 only: {len(all_reviews)} total)")
            
            # Check pagination
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")
            page_num += 1
            
            # Continue until we have enough 2023 data or no more pages
            if has_next_page:
                time.sleep(0.5)
        
        print(f"\n{'=' * 70}")
        print(f"✅ Scraping complete! Retrieved {len(all_reviews)} reviews from 2023.")
        
        # Sentiment distribution
        if sentiment_pipeline:
            positive_count = sum(1 for r in all_reviews if r.get('sentiment') == 'POSITIVE')
            negative_count = sum(1 for r in all_reviews if r.get('sentiment') == 'NEGATIVE')
            print(f"\n💭 Sentiment Analysis Summary:")
            print(f"   • Positive: {positive_count} ({positive_count/len(all_reviews)*100:.1f}%)")
            print(f"   • Negative: {negative_count} ({negative_count/len(all_reviews)*100:.1f}%)")
            if positive_count > negative_count * 3:
                print(f"   ⚠️  Note: High positive ratio is from the actual website data.")
        
    except requests.RequestException as e:
        print(f"\n❌ Network error during scraping: {e}")
        print("Please check your internet connection and try again.")
        return []
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return []
    
    # Save to JSON file
    if all_reviews:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(all_reviews, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Saved {len(all_reviews)} reviews to data.json")
        
        # Show data statistics
        print(f"\n📊 Dataset Statistics:")
        print(f"   • Total reviews: {len(all_reviews)}")
        
        # Date range
        dates = [datetime.strptime(r['date'], "%Y-%m-%d") for r in all_reviews]
        min_date = min(dates)
        max_date = max(dates)
        print(f"   • Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
        
        # Monthly distribution
        from collections import Counter
        months = [d.strftime("%Y-%m") for d in dates]
        month_counts = Counter(months)
        
        print(f"\n📅 Reviews by Month:")
        for month in sorted(month_counts.keys()):
            count = month_counts[month]
            bar = "█" * min(count // 2, 50)  # Visual bar chart
            print(f"   {month}: {count:3d} {bar}")
        
        # Rating distribution
        ratings = [r.get('rating', 0) for r in all_reviews]
        rating_counts = Counter(ratings)
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        print(f"\n⭐ Rating Distribution:")
        for rating in sorted(rating_counts.keys(), reverse=True):
            count = rating_counts[rating]
            stars = "⭐" * rating
            bar = "█" * (count // 2)
            print(f"   {stars} ({rating}): {count:3d} {bar}")
        print(f"   Average: {avg_rating:.2f}/5")
        
        # Sample review
        print(f"\n📝 Sample Review:")
        sample = all_reviews[0]
        print(f"   Title: {sample['title']}")
        print(f"   Date: {sample['date']}")
        print(f"   Rating: {'⭐' * sample['rating']}")
        print(f"   Text: {sample['text'][:100]}...")
        
        print(f"\n{'=' * 70}")
        print(f"✅ SUCCESS! Data ready for Streamlit app.")
        print(f"   Run: streamlit run app.py")
        
    else:
        print("\n⚠️  No reviews were scraped. Check your internet connection.")
        print("   The API might be temporarily unavailable.")
    
    return all_reviews

if __name__ == "__main__":
    reviews = scrape_data()
    if reviews:
        print(f"\n🎉 Scraping job completed successfully!")
    else:
        print(f"\n❌ Scraping failed. Please try again.")
