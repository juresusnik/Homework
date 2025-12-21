import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Make sentiment analysis optional - only load if needed
sentiment_pipeline = None

def load_sentiment_model():
    """Load sentiment model on demand"""
    global sentiment_pipeline
    if sentiment_pipeline is None:
        try:
            from transformers import pipeline
            print("🤖 Loading Hugging Face sentiment model...")
            sentiment_pipeline = pipeline("sentiment-analysis", 
                                         model="distilbert-base-uncased-finetuned-sst-2-english",
                                         device=-1)  # CPU
            print("✅ Model loaded successfully!\n")
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            sentiment_pipeline = None
    return sentiment_pipeline

def scrape_reviews():
    """
    Scrapes review data from web-scraping.dev using GraphQL API.
    Fetches ALL reviews and filters for year 2023.
    """
    print("="*70)
    print("📝 SCRAPING REVIEWS")
    print("="*70)
    print("🌐 Starting web scraping from https://web-scraping.dev/reviews...")
    print("🎯 Target: All reviews from year 2023\n")
    
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
        batch_size = 50
        max_pages = 20
        
        while has_next_page and page_num <= max_pages:
            print(f"📄 Fetching page {page_num}...")
            
            variables = {"first": batch_size}
            if cursor:
                variables["after"] = cursor
            
            payload = {
                "query": query_template,
                "variables": variables
            }
            
            response = requests.post(graphql_url, json=payload, timeout=15, verify=False)
            response.raise_for_status()
            
            data = response.json()
            
            if "errors" in data:
                print(f"❌ GraphQL Error: {data['errors']}")
                break
            
            edges = data.get("data", {}).get("reviews", {}).get("edges", [])
            page_info = data.get("data", {}).get("reviews", {}).get("pageInfo", {})
            
            if not edges:
                break
            
            for edge in edges:
                node = edge.get("node", {})
                
                review_id = node.get("rid", "unknown")
                text = node.get("text", "")
                rating = node.get("rating", 0)
                date_str = node.get("date", "")
                
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    
                    if date_obj.year != 2023:
                        continue
                        
                except ValueError:
                    continue
                
                title = " ".join(word.capitalize() for word in review_id.rsplit('-', 1)[0].split('-'))
                title = f"{title} Review"
                
                sentiment_label = "UNKNOWN"
                sentiment_score = 0.0
                
                # Load and use sentiment model
                model = load_sentiment_model()
                if model and text:
                    try:
                        result = model(text[:512], truncation=True)[0]
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
            
            print(f"   ✅ Fetched {len(edges)} reviews (2023 only: {len(all_reviews)} total)")
            
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")
            page_num += 1
            
            if has_next_page:
                time.sleep(0.5)
        
        print(f"\n✅ Scraping complete! Retrieved {len(all_reviews)} reviews from 2023.")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        return []
    
    return all_reviews


def scrape_products():
    """
    Scrapes product data from web-scraping.dev/products using Selenium or BeautifulSoup fallback.
    """
    print("\n" + "="*70)
    print("📦 SCRAPING PRODUCTS")
    print("="*70)
    
    all_products = []
    
    # Try Selenium first
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("Trying Selenium to scrape products...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # There are 6 pages of products
        for page in range(1, 7):
            print(f"📄 Fetching page {page}...")
            
            url = f"https://web-scraping.dev/products?page={page}"
            driver.get(url)
            
            # Wait for page to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".product"))
                )
            except:
                print(f"No products found on page {page}, skipping...")
                continue
            
            # Find all product elements
            product_elements = driver.find_elements(By.CSS_SELECTOR, ".product")
            
            for product_elem in product_elements:
                try:
                    # Extract product name from h3 > a
                    name_elem = product_elem.find_element(By.CSS_SELECTOR, "h3 a")
                    name = name_elem.text.strip()
                    product_url = name_elem.get_attribute("href")
                    
                    # Extract product ID from URL
                    product_id = product_url.split('/')[-1] if product_url else f"product-{len(all_products) + 1}"
                    
                    # Extract price from .price div
                    price_elem = product_elem.find_element(By.CSS_SELECTOR, ".price")
                    price_text = price_elem.text.strip()
                    price = f"${price_text}" if not price_text.startswith('$') else price_text
                    
                    # Extract description from .short-description
                    desc_elem = product_elem.find_element(By.CSS_SELECTOR, ".short-description")
                    description = desc_elem.text.strip()
                    
                    # Extract image
                    try:
                        img_elem = product_elem.find_element(By.CSS_SELECTOR, "img")
                        image = img_elem.get_attribute("src")
                    except:
                        image = ""
                    
                    product = {
                        "id": f"product-{product_id}",
                        "name": name,
                        "url": product_url,
                        "price": price,
                        "description": description,
                        "image": image,
                        "section": "Products"
                    }
                    
                    all_products.append(product)
                    
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            print(f"   ✅ Found {len(product_elements)} products on page {page}")
            # Small delay between pages
            time.sleep(0.5)
        
        driver.quit()
        print(f"\n✅ Total products scraped: {len(all_products)}")
        return all_products
        
    except Exception as e:
        print(f"⚠️  Selenium failed: {e}")
        print("Falling back to BeautifulSoup method...")
    
    # Fallback to BeautifulSoup method
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        for page in range(1, 7):
            url = f"https://web-scraping.dev/products?page={page}"
            print(f"📄 Fetching page {page} with BeautifulSoup...")
            
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ Failed to fetch page {page}")
                break
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all product cards
            products = soup.find_all('div', class_='product')
            
            if not products:
                print(f"No products found on page {page}, stopping.")
                break
            
            for product in products:
                try:
                    # Get product name
                    h3 = product.find('h3')
                    name_link = h3.find('a') if h3 else None
                    name = name_link.text.strip() if name_link else "Unknown Product"
                    product_url = name_link.get('href', '') if name_link else ''
                    
                    # Extract product ID from URL
                    product_id = product_url.split('/')[-1] if product_url else str(len(all_products) + 1)
                    
                    # Get description
                    desc_elem = product.find('div', class_='short-description')
                    description = desc_elem.text.strip() if desc_elem else ""
                    
                    # Get price
                    price_elem = product.find('div', class_='price')
                    price = f"${price_elem.text.strip()}" if price_elem else "N/A"
                    
                    # Get image
                    img = product.find('img')
                    image = img.get('src', '') if img else ''
                    
                    all_products.append({
                        'id': f'product-{product_id}',
                        'name': name,
                        'url': product_url,
                        'price': price,
                        'description': description,
                        'image': image,
                        'section': 'Products'
                    })
                except Exception as e:
                    print(f"Error parsing product: {e}")
                    continue
            
            print(f"   ✅ Found {len(products)} products on page {page}")
            time.sleep(0.3)
        
        print(f"\n✅ Total products scraped: {len(all_products)}")
        
    except Exception as e:
        print(f"\n❌ Error during product scraping: {e}")
        return []
    
    return all_products


def scrape_testimonials():
    """
    Scrapes testimonial data from web-scraping.dev/testimonials using Selenium.
    Handles infinite scroll to load all testimonials.
    """
    print("\n" + "="*70)
    print("💬 SCRAPING TESTIMONIALS")
    print("="*70)
    
    all_testimonials = []
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from selenium.common.exceptions import NoSuchElementException
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("Using Selenium to scrape JavaScript-loaded content...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Navigating to testimonials page...")
        driver.get('https://web-scraping.dev/testimonials')
        
        # Wait for initial load
        time.sleep(2)
        
        # Handle infinite scroll - scroll down multiple times to load all testimonials
        print("Scrolling to load all testimonials...")
        last_height = driver.execute_script("return document.body.scrollHeight")
        max_scrolls = 15  # Increase to load all testimonials
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)  # Wait for content to load
            
            # Check if we've reached the bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Reached bottom of page")
                break
            
            last_height = new_height
            scroll_count += 1
            print(f"Scrolled {scroll_count} times")
        
        # Extract testimonials
        print("Extracting testimonials...")
        
        # Use the correct selector: .testimonial (not .testimonial-card)
        testimonial_elements = driver.find_elements(By.CSS_SELECTOR, ".testimonial")
        
        if not testimonial_elements:
            # Try alternative selectors
            testimonial_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='testimonial']")
        
        print(f"Found {len(testimonial_elements)} testimonial elements")
        
        for testimonial_elem in testimonial_elements:
            try:
                # Try to find the text element
                try:
                    text_elem = testimonial_elem.find_element(By.CSS_SELECTOR, ".text, p.text, p")
                    text = text_elem.text.strip()
                except NoSuchElementException:
                    # Fallback to full text
                    text = testimonial_elem.text.strip()
                
                if not text:
                    continue
                
                author = "Anonymous"
                
                # Try to find author element
                try:
                    author_elem = testimonial_elem.find_element(By.CSS_SELECTOR, ".author, .testimonial-author")
                    author = author_elem.text.strip()
                except NoSuchElementException:
                    pass
                
                # Count stars - look for SVG elements in the .rating span
                star_svgs = testimonial_elem.find_elements(By.CSS_SELECTOR, ".rating svg")
                rating = len(star_svgs) if star_svgs else 5
                
                if text and len(text) > 5:
                    testimonial = {
                        "id": f"testimonial-{len(all_testimonials) + 1}",
                        "text": text,
                        "author": author,
                        "rating": rating,
                        "section": "Testimonials"
                    }
                    all_testimonials.append(testimonial)
                    
            except Exception as e:
                print(f"Error parsing testimonial: {e}")
                continue
        
        driver.quit()
        print(f"✅ Successfully scraped {len(all_testimonials)} real testimonials")
        
    except Exception as e:
        print(f"❌ Error during testimonial scraping: {e}")
        print("No testimonials will be added (no fake data)")
        return []
    
    return all_testimonials


def main():
    """
    Main function to scrape all data and save to JSON file.
    """
    print("\n" + "🚀 " * 35)
    print("   WEB SCRAPING - COMPLETE DATA COLLECTION")
    print("🚀 " * 35 + "\n")
    
    # Scrape all three sections
    reviews = scrape_reviews()
    products = scrape_products()
    testimonials = scrape_testimonials()
    
    # Combine all data
    all_data = {
        'reviews': reviews,
        'products': products,
        'testimonials': testimonials
    }
    
    # Save to JSON file
    print("\n" + "="*70)
    print("💾 SAVING DATA")
    print("="*70)
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved all data to data.json")
    print(f"\n📊 Summary:")
    print(f"   • Reviews: {len(reviews)}")
    print(f"   • Products: {len(products)}")
    print(f"   • Testimonials: {len(testimonials)}")
    print(f"   • Total items: {len(reviews) + len(products) + len(testimonials)}")
    
    print("\n" + "✨ " * 35)
    print("   SCRAPING COMPLETED SUCCESSFULLY!")
    print("✨ " * 35 + "\n")


if __name__ == "__main__":
    main()
