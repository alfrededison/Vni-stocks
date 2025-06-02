# VNI Stocks

A fullstack stock analysis application with a **Flask backend** and a **React frontend**.

---

## Project Structure

```
.
├── backend/    # Python Flask API for data, signals, and stock filtering
│   ├── app.py
│   ├── builder.py
│   ├── const.py
│   ├── discord.py
│   ├── tcbs.py
│   ├── vci.py
│   ├── data.csv
│   ├── all.csv
│   ├── time_records.json
│   ├── ta/         # Technical analysis utilities
│   ├── Pipfile
│   ├── Pipfile.lock
│   └── ...
├── frontend/   # React app for UI
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Home.js
│   │   │   └── Stocks.js
│   │   ├── App.js
│   │   ├── api.js
│   │   ├── index.js
│   │   ├── index.css
│   │   └── table.css
│   ├── package.json
│   └── configs.json.example
├── README.md
└── .gitignore
```

---

## Backend

- **Framework:** Flask (Python)
- **Location:** [`backend/`](backend/)
- **Main entry:** [`backend/app.py`](backend/app.py)
- **Key APIs:**
  - `/signals` — Get latest time records and signal data
  - `/stocks` — Get filtered stock data from `all.csv`
  - `/build` — Trigger data retrieval and signal building
  - `/filter` — Trigger stock filtering
- **Data files:** `data.csv`, `all.csv`, `time_records.json`

### Setup

```sh
cd backend
pip install pipenv
pipenv install
pipenv run python app.py
```

---

## Frontend

- **Framework:** React
- **Location:** [`frontend/`](frontend/)
- **Main entry:** [`frontend/src/App.js`](frontend/src/App.js)
- **Routes:**
  - `/` — Home: signal table and chart
  - `/stocks` — Stocks: filtered stock data table

### Setup

```sh
cd frontend
cp configs.json.example src/configs.json   # Edit API_BASE_URL if needed
npm install
npm start
```

---

## Usage

- Start the backend server (default: http://localhost:5000)
- Start the frontend (default: http://localhost:3000)
- The frontend will call the backend API as configured in `frontend/configs.json`

---

## Notes

- For deployment, configure CORS and environment variables as needed.
- Data and signals are generated and filtered by backend logic in [`builder.py`](backend/builder.py) and related modules.

---

## License

MIT