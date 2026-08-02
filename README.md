# CivicTrace

A streamlined tool for municipal staff to document, search, and analyse council meeting reports and voting outcomes.

Built for Cessnock City Council-style minutes. Upload a set of minutes and the app will detect motions, titles, movers/seconders, FOR/AGAINST votes, and conflict-of-interest disclosures for you to review before importing.

## Features

- **Upload Minutes** – PDF or text. Automatically extracts motions, votes and conflicts (with a review step so data stays accurate)
- **Add Report** – Manually record motions with individual councillor votes
- **Dashboard** – Overview of recent reports and minutes
- **Search** – Full-text search across reports and uploaded minutes
- **Voting Analysis** – Outcomes and per-councillor voting patterns
- **Manage & Delete** – Permanently delete reports or minutes that were entered incorrectly (with confirmation)

## Local run

```bash
cd civictrace
pip install -r requirements.txt
streamlit run app.py
```

Data is stored in a local SQLite file (`civictrace.db`).

## Deploy to Streamlit Community Cloud (recommended)

1. Create a new public or private repository on GitHub.
2. Upload the entire contents of the `civictrace` folder into the **root** of the repository.
3. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
4. Click **New app**.
5. Select your repository and branch (`main`).
6. Set the **Main file path** to:
   ```
   app.py
   ```
7. Click **Deploy**.

Your app will be live in a couple of minutes at a URL like:
`https://your-app-name.streamlit.app`

### Notes for Streamlit Cloud

- The free tier restarts the app periodically. The SQLite database is wiped on restart.  
  This is usually fine for a personal review tool. If you later need permanent storage we can switch to a cloud database (Supabase, Turso, etc.).
- No secrets or API keys are required for the current version.

## Project structure

```
civictrace/
├── app.py                 # Entry point + navigation
├── database.py            # SQLite helpers
├── parser.py              # Minutes extraction (motions, votes, conflicts)
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Upload_Minutes.py
│   ├── 3_Add_Report.py
│   ├── 4_Search.py
│   ├── 5_Analysis.py
│   └── 6_Manage_Data.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Requirements

- streamlit
- pypdf
- pandas
