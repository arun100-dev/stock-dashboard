# 🚀 Stock Intelligence Dashboard  
*A Mini Financial Data Platform with Analytics & ML Insights*

---

## 📌 Overview
This project is a full-stack Stock Data Intelligence Dashboard built using FastAPI for the JarNox internship assignment.

It demonstrates:
- Real-world financial data handling  
- REST API development  
- Data analytics & visualization  
- Basic machine learning forecasting  

The system fetches NSE stock data using yfinance, processes it, stores it in SQLite, and serves insights via APIs and an interactive dashboard.

---

## 🛠️ Tech Stack
- Backend: FastAPI  
- Database: SQLite  
- Data Source: yfinance  
- Data Processing: Pandas, NumPy  
- Frontend: HTML, CSS, JavaScript, Chart.js  
- ML: Linear Regression (custom implementation)  
- Deployment: Docker ready  

---

## ⚙️ Setup

### Docker (Recommended)
docker-compose up --build

### Local Setup
python -m venv venv  
venv\Scripts\activate  
pip install -r requirements.txt  
uvicorn main:app --reload  

App: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs  

---

## 🔌 API Endpoints
- /companies → List companies  
- /data/{symbol} → Last N days data  
- /summary/{symbol} → 52-week stats  
- /compare → Compare two stocks  
- /predict/{symbol} → ML forecast  

---

## 📊 Features
- Stock price visualization  
- Moving average analysis  
- Volatility calculation  
- Stock comparison  
- ML-based prediction  

---

## 🧠 Machine Learning
Implemented custom Linear Regression (no sklearn) to predict future stock prices and trends.

---

## 📈 Dashboard
- Interactive charts  
- Company selection  
- Compare mode  
- Forecast mode  

---

## 📂 Project Structure

stock-dashboard/
│
├── main.py                  # FastAPI entry point  
├── app/  
│   ├── database.py          # Database setup  
│   ├── seed.py              # Data ingestion (yfinance)  
│   └── routes/  
│       ├── stocks.py        # Core APIs  
│       ├── analytics.py     # Comparison & insights  
│       └── predictions.py   # ML predictions  
│
├── templates/  
│   └── index.html           # Frontend UI  
│
├── static/                  # CSS/JS assets  
├── data/                    # SQLite database  
├── Dockerfile  
├── docker-compose.yml  
├── requirements.txt  
└── README.md  

---

## 🏢 Supported Stocks
INFY, TCS, RELIANCE, HDFCBANK, WIPRO, ICICIBANK, SBIN, BAJFINANCE, ASIANPAINT, MARUTI  

---

## 💡 Highlights
- Clean modular architecture  
- Real financial data integration  
- Full-stack implementation  
- ML integration  

---

## 🙌 Conclusion
This project demonstrates my ability to build scalable, data-driven applications with real-world relevance.

⭐ Thank you for reviewing my project!
