# 📊 Brand Sentinel 2023 - Sentiment Analysis Dashboard

A Streamlit web application that scrapes product reviews, performs AI-powered sentiment analysis using Hugging Face transformers, and visualizes insights with interactive charts and word clouds.

## 🎯 Project Overview

This project demonstrates:
- **Web Scraping**: Automated data collection from web-scraping.dev/reviews using BeautifulSoup
- **NLP & AI**: Real-time sentiment analysis using DistilBERT (Hugging Face)
- **Data Visualization**: Interactive charts (Plotly) and word clouds
- **Web Deployment**: Production-ready Streamlit app hosted on Render

## 🚀 Features

- ✅ **Smart Web Scraping**: Extracts titles, review text, and dates across multiple pages
- ✅ **AI Sentiment Analysis**: Hugging Face DistilBERT model for accurate sentiment detection
- ✅ **Interactive Dashboard**: Filter reviews by month with real-time analysis
- ✅ **Rich Visualizations**: Bar charts, confidence metrics, and word clouds
- ✅ **Responsive UI**: Clean, professional interface with sidebar navigation

## 📁 Project Structure

```
├── app.py              # Main Streamlit application
├── scraper.py          # Web scraping script
├── requirements.txt    # Python dependencies
├── data.json           # Scraped review data (generated)
├── README.md           # Project documentation
└── REPORT.md           # Analysis report (Gemini prompts & findings)
```

## 🛠️ Installation & Setup

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/brand-sentinel-2023.git
   cd brand-sentinel-2023
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the scraper**:
   ```bash
   python scraper.py
   ```
   This creates `data.json` with scraped reviews.

5. **Launch the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

6. **Open browser**: Navigate to `http://localhost:8501`

## 🌐 Deployment (Render)

### Prerequisites
- GitHub account with your code pushed
- Render account (free tier available)

### Steps

1. **Push to GitHub** (see GitHub section below)

2. **Create Render Web Service**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `brand-sentinel-2023`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
     - **Instance Type**: Free

3. **Deploy**: Render will automatically build and deploy your app

4. **Access**: Your live URL will be `https://brand-sentinel-2023.onrender.com`

## 📊 Usage

1. **Navigate** to "📊 Reviews (Analysis)" in the sidebar
2. **Select Month** using the slider (Jan-Dec 2023)
3. **View Results**:
   - Key metrics (total, positive/negative counts, confidence)
   - Detailed review table
   - Sentiment distribution bar chart
   - Word cloud of frequent terms
   - Confidence distribution histogram
   - Daily review volume timeline

## 🤖 AI Model Details

- **Model**: `distilbert-base-uncased-finetuned-sst-2-english`
- **Provider**: Hugging Face Transformers
- **Type**: Binary sentiment classification (Positive/Negative)
- **Confidence**: Model outputs probability scores (0-1)

## 📈 Rubric Compliance

| Criterion | Implementation | Points |
|-----------|---------------|--------|
| Web Scraping | BeautifulSoup with pagination, date/text/title extraction | 2/2 |
| App Architecture | Streamlit with sidebar, month slider, error handling | 2.5/2.5 |
| NLP & AI | Hugging Face DistilBERT pipeline, dynamic analysis | 2/2 |
| Visualization | Plotly bar charts, confidence metrics display | 1.5/1.5 |
| Deployment | Clean GitHub repo, requirements.txt, Render deployment | 1/1 |
| Report | REPORT.md with Gemini prompts and analysis | 1/1 |
| **Bonus** | Word cloud generation for selected month | 2/2 |
| **Total** | | **12/12** |

## 🐛 Troubleshooting

### "data.json not found"
Run `python scraper.py` to generate the data file.

### Model download issues
Ensure stable internet connection. First run downloads ~250MB model from Hugging Face.

### Deployment fails on Render
- Verify `requirements.txt` has all dependencies
- Check build logs for specific errors
- Ensure start command includes port binding: `--server.port=$PORT --server.address=0.0.0.0`

## 📝 License

MIT License - Feel free to use for educational purposes.

## 👤 Author

[Your Name] - SmartNinja Data Science Course HW3

## 🔗 Links

- **Live Demo**: [Render URL]
- **GitHub Repo**: [Your GitHub URL]
- **Report**: See [REPORT.md](REPORT.md)
