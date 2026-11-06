# For You, My All-Rounder

A light-mode football analytics dashboard built with Python, pandas, Plotly and Streamlit. It analyzes the supplied 2025/26 player-statistics workbook across the Premier League, La Liga, Bundesliga, Serie A and Ligue 1.

## Dashboard views

- **Executive overview:** headline KPIs, league comparison, position contribution and leading clubs.
- **Player performance:** top attacking contributors, age analysis, per-90 efficiency and player detail.
- **Team and league:** club contribution profiles, position mix, available defensive actions and discipline.
- **Scouting comparison:** multi-player radar and per-90 comparison with a documented project-defined score.

## Run locally

```powershell
cd C:\Users\User\football
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Data handling

- Source grain is retained at one row per supplied player-club record.
- Per-90 metrics use recorded minutes as the denominator.
- Shot accuracy is shots on target divided by shots.
- The scouting score is a project-defined percentile score for qualified outfield players: 45% contributions per 90, 15% shot accuracy, 25% defensive actions per 90 and 15% minutes.
- The supplied dataset does not contain match results, standings, possession, clearances or goals conceded. The application does not infer those fields.

## Validation

Run the data reconciliation tests with:

```powershell
python -m unittest discover -s tests -v
```

Expected source controls are 2,839 rows, 2,687 distinct players, 4,714 goals, 3,291 assists and 3,459,549 minutes.

