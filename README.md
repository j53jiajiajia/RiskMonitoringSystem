# 📊 Risk Monitoring System

This project is a mini risk monitoring system with real-time data fetching, margin calculations, and an interactive dashboard.

---
## 📊 Demo Video
https://drive.google.com/file/d/1avWxSW0X0639ENk6BC1WJo6xF_89KgGR/view?usp=drive_link


## 🧱 Architecture Overview

```
+--------------+           +-------------+           +--------------+
|              |           |             |           |              |
|  Frontend    +<-------->+    Backend   +<-------->+    Database   |
|  (React.js)  |           |   (Flask)   |           | (PostgreSQL) |
+--------------+           +-------------+           +--------------+
```

- **Frontend**: React + Recharts + Axios
- **Backend**: Python Flask + Psycopg2 + yFinance
- **Database**: PostgreSQL

---

## 🚀 Getting Started

### 1. Install Dependencies
Make sure Python, Node.js, and PostgreSQL are installed locally.

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd frontend
npm install
```

### 2. Start the System (Manual Method)

#### ✅ Terminal 1: Initialize database
```bash
python -m app.database
```

#### ✅ Terminal 2: Fetch latest market prices
```bash
python -m app.fetch_market_data
```

#### ✅ Terminal 3: Run backend Flask API
```bash
python -m app.main
```

#### ✅ Terminal 4: Run frontend with Vite
```bash
cd frontend
npm run dev
```

---

## ⚙️ Tech Stack

| Component | Stack |
|----------|--------|
| Frontend | React + Recharts + Vite |
| Backend  | Flask + psycopg2 + yfinance |
| Database | PostgreSQL |

- **PostgreSQL** is chosen for strong relational modeling.
- **Flask** is lightweight and easy to use with REST APIs.
- **React + Vite** provide fast and reactive UI development.

---

## 🧪 Testing & Validation

- Market data is fetched via yFinance (1-minute intraday prices).
- Margin status is recalculated every 10 seconds.
- Add new positions from the frontend and watch dashboard update live.

---

## 🧩 Usage Notes

- Go to `http://localhost:5173` to view the dashboard.
- Backend endpoints available at `http://localhost:5000/api/...`
- Available API endpoints:
  - `GET /api/clients`
  - `GET /api/market-data`
  - `GET /api/positions/<client_id>`
  - `GET /api/margin-status/<client_id>`
  - `POST /api/positions`

---

## ⚠️ Known Limitations

- No user authentication (assumes local-only usage).
- yFinance API may be rate-limited or return stale data.
- Not deployed (manual multi-terminal launch) because of time limitation. I would like to deploy it using Docker if you can give me more time.

---

## 🙌 Acknowledgments

- Yahoo Finance for data

