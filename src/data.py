from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "Football_Players_Stats_2025_2026.xlsx"
)

LEAGUE_NAMES = {
    "eng Premier League": "Premier League",
    "es La Liga": "La Liga",
    "de Bundesliga": "Bundesliga",
    "it Serie A": "Serie A",
    "fr Ligue 1": "Ligue 1",
}

POSITION_NAMES = {
    "GK": "Goalkeeper",
    "DF": "Defender",
    "MF": "Midfielder",
    "FW": "Forward",
}

NUMERIC_COLUMNS = [
    "Age",
    "MP",
    "Starts",
    "Min",
    "90s",
    "Gls",
    "Ast",
    "G+A",
    "CrdY",
    "CrdR",
    "Sh",
    "SoT",
    "SoT%",
    "Sh/90",
    "SoT/90",
    "Int",
    "TklW",
    "Fls",
    "Fld",
    "Crs",
    "Off",
    "PPM",
    "Saves",
    "Save%",
    "CS",
]


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    result = numerator.div(denominator.replace(0, np.nan))
    return result.replace([np.inf, -np.inf], np.nan).fillna(0.0)


def load_player_data(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load and prepare the source table without changing its source grain."""
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Football dataset not found: {source}")

    frame = pd.read_excel(source, sheet_name="Player Stats", skiprows=1)
    required = {
        "Player",
        "Squad",
        "Comp",
        "Pos",
        "Age",
        "Min",
        "Gls",
        "Ast",
        "Sh",
        "SoT",
        "Int",
        "TklW",
        "CrdY",
        "CrdR",
    }
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")

    frame = frame.copy()
    for column in NUMERIC_COLUMNS:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame["League"] = frame["Comp"].map(LEAGUE_NAMES).fillna(frame["Comp"])
    frame["Primary Position Code"] = frame["Pos"].astype(str).str.split(",").str[0]
    frame["Position Group"] = (
        frame["Primary Position Code"].map(POSITION_NAMES).fillna("Other")
    )
    frame["Season"] = "2025/26"
    frame["Goal Contributions"] = frame["Gls"].fillna(0) + frame["Ast"].fillna(0)
    frame["Goals Per 90"] = _safe_divide(frame["Gls"] * 90, frame["Min"])
    frame["Assists Per 90"] = _safe_divide(frame["Ast"] * 90, frame["Min"])
    frame["Contributions Per 90"] = _safe_divide(
        frame["Goal Contributions"] * 90, frame["Min"]
    )
    frame["Shot Accuracy"] = _safe_divide(frame["SoT"], frame["Sh"])
    frame["Defensive Actions"] = frame["Int"].fillna(0) + frame["TklW"].fillna(0)
    frame["Defensive Actions Per 90"] = _safe_divide(
        frame["Defensive Actions"] * 90, frame["Min"]
    )
    frame["Discipline Points"] = frame["CrdY"].fillna(0) + 3 * frame["CrdR"].fillna(0)
    return frame


def apply_filters(
    frame: pd.DataFrame,
    leagues: Iterable[str] | None = None,
    clubs: Iterable[str] | None = None,
    positions: Iterable[str] | None = None,
) -> pd.DataFrame:
    filtered = frame
    if leagues:
        filtered = filtered[filtered["League"].isin(list(leagues))]
    if clubs:
        filtered = filtered[filtered["Squad"].isin(list(clubs))]
    if positions:
        filtered = filtered[filtered["Position Group"].isin(list(positions))]
    return filtered.copy()


def overview_metrics(frame: pd.DataFrame) -> dict[str, int | float]:
    shots = frame["Sh"].fillna(0).sum()
    shots_on_target = frame["SoT"].fillna(0).sum()
    return {
        "players": int(frame["Player"].nunique()),
        "goals": int(frame["Gls"].fillna(0).sum()),
        "assists": int(frame["Ast"].fillna(0).sum()),
        "contributions": int(frame["Goal Contributions"].fillna(0).sum()),
        "minutes": int(frame["Min"].fillna(0).sum()),
        "shot_accuracy": float(shots_on_target / shots) if shots else 0.0,
    }


def scouting_table(frame: pd.DataFrame, minimum_minutes: int) -> pd.DataFrame:
    """Return qualified outfield players with a transparent project-defined score."""
    qualified = frame[
        (frame["Min"].fillna(0) >= minimum_minutes)
        & (frame["Position Group"] != "Goalkeeper")
    ].copy()
    if qualified.empty:
        qualified["Scouting Score"] = pd.Series(dtype=float)
        return qualified

    components = {
        "Contributions Per 90": 0.45,
        "Shot Accuracy": 0.15,
        "Defensive Actions Per 90": 0.25,
        "Min": 0.15,
    }
    score = pd.Series(0.0, index=qualified.index)
    for metric, weight in components.items():
        score += qualified[metric].rank(pct=True, method="average") * weight
    qualified["Scouting Score"] = (score * 100).round(1)
    return qualified.sort_values("Scouting Score", ascending=False)

