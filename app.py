from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    age_output_scatter,
    comparison_bars,
    defensive_by_league,
    discipline_by_league,
    efficiency_scatter,
    league_goals_assists,
    player_output,
    position_club_heatmap,
    position_contributions,
    scouting_radar,
    team_contributions,
    top_clubs,
)
from src.data import (
    DEFAULT_DATA_PATH,
    apply_filters,
    load_player_data,
    overview_metrics,
    scouting_table,
)


st.set_page_config(
    page_title="For You, My All-Rounder",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)


CSS = """
<style>
    :root {
        --navy: #0f172a;
        --blue: #2563eb;
        --cyan: #06b6d4;
        --violet: #7c3aed;
        --green: #059669;
        --muted: #64748b;
        --line: rgba(148, 163, 184, 0.28);
        --glass: rgba(255, 255, 255, 0.68);
        --page: #f4f7ff;
    }
    html { scroll-behavior: smooth; }
    .stApp {
        color: var(--navy);
        background:
            radial-gradient(circle at 82% 4%, rgba(124, 58, 237, 0.17), transparent 29rem),
            radial-gradient(circle at 12% 30%, rgba(6, 182, 212, 0.17), transparent 32rem),
            radial-gradient(circle at 74% 88%, rgba(37, 99, 235, 0.12), transparent 31rem),
            linear-gradient(145deg, #f8fbff 0%, #eef3ff 48%, #f7f5ff 100%);
        background-attachment: fixed;
    }
    .stApp::before, .stApp::after {
        content: ""; position: fixed; z-index: 0; pointer-events: none; border-radius: 999px;
        filter: blur(4px); opacity: .72; animation: drift 14s ease-in-out infinite alternate;
    }
    .stApp::before {
        width: 270px; height: 270px; right: 4vw; top: 12vh;
        background: radial-gradient(circle at 32% 28%, rgba(255,255,255,.95), rgba(37,99,235,.24) 38%, rgba(124,58,237,.10) 68%, transparent 70%);
    }
    .stApp::after {
        width: 190px; height: 190px; left: 21vw; bottom: 4vh;
        background: radial-gradient(circle at 35% 30%, rgba(255,255,255,.9), rgba(6,182,212,.20) 42%, transparent 72%);
        animation-delay: -6s;
    }
    @keyframes drift { from { transform: translate3d(0,-12px,0) rotate(-4deg); } to { transform: translate3d(18px,20px,0) rotate(8deg); } }
    @keyframes floatBall { 0%,100% { transform: translateY(0) rotate(-8deg); } 50% { transform: translateY(-13px) rotate(8deg); } }
    @keyframes shimmer { 0% { transform: translateX(-160%) skewX(-20deg); } 100% { transform: translateX(330%) skewX(-20deg); } }
    @keyframes reveal { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,.62); border-right: 1px solid rgba(255,255,255,.8);
        backdrop-filter: blur(24px) saturate(145%); -webkit-backdrop-filter: blur(24px) saturate(145%);
        box-shadow: 14px 0 40px rgba(30,64,175,.07);
    }
    [data-testid="stHeader"] { background: rgba(244,247,255,.46); backdrop-filter: blur(18px); }
    [data-testid="stMainBlockContainer"] { position: relative; z-index: 1; }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1520px; }
    h1, h2, h3 { color: var(--navy); letter-spacing: -0.02em; }
    h1 { font-size: clamp(2rem, 3.2vw, 3.45rem) !important; margin: 0 !important; line-height: 1.03 !important; }
    h2 { font-size: 1.35rem !important; margin-top: 1.2rem !important; }
    .hero-shell {
        position: relative; overflow: hidden; isolation: isolate; min-height: 190px; display: flex;
        align-items: center; justify-content: space-between; gap: 28px; padding: 28px 34px; margin-bottom: 24px;
        border: 1px solid rgba(255,255,255,.78); border-radius: 26px;
        background: linear-gradient(125deg, rgba(255,255,255,.80), rgba(255,255,255,.48));
        box-shadow: 0 24px 70px rgba(37,99,235,.12), inset 0 1px 0 rgba(255,255,255,.95);
        backdrop-filter: blur(25px) saturate(150%); -webkit-backdrop-filter: blur(25px) saturate(150%);
        animation: reveal .65s ease both;
    }
    .hero-shell::before { content:""; position:absolute; width:360px; height:360px; right:-80px; top:-185px; border-radius:50%; background: radial-gradient(circle, rgba(124,58,237,.20), transparent 68%); z-index:-1; }
    .hero-copy { max-width: 900px; }
    .page-kicker { display:inline-flex; color:#1d4ed8; background:rgba(219,234,254,.72); border:1px solid rgba(147,197,253,.62); border-radius:999px; padding:7px 12px; font-weight:750; font-size:.72rem; text-transform:uppercase; letter-spacing:.1em; margin-bottom:12px; }
    .page-subtitle { color: var(--muted); font-size: 1rem; line-height:1.6; margin: 14px 0 0; max-width:850px; }
    .hero-ball {
        width: 126px; height: 126px; min-width:126px; border-radius:50%; position:relative;
        background: radial-gradient(circle at 31% 25%, #ffffff 0 7%, #dbeafe 14%, #60a5fa 36%, #2563eb 58%, #312e81 82%);
        box-shadow: inset -18px -22px 32px rgba(15,23,42,.35), inset 12px 12px 24px rgba(255,255,255,.46), 0 28px 55px rgba(37,99,235,.30), 0 0 0 10px rgba(255,255,255,.28);
        animation: floatBall 5s ease-in-out infinite;
    }
    .hero-ball::before, .hero-ball::after { content:""; position:absolute; border:2px solid rgba(255,255,255,.34); border-radius:50%; inset:24px 11px; transform:rotate(42deg); }
    .hero-ball::after { inset:12px 30px; transform:rotate(-34deg); }
    .metric-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(155px,1fr)); gap:14px; margin: 0 0 22px; animation: reveal .7s .08s ease both; }
    .metric-card {
        position:relative; overflow:hidden; transform-style:preserve-3d;
        background: linear-gradient(145deg, rgba(255,255,255,.82), rgba(255,255,255,.48));
        border:1px solid rgba(255,255,255,.86); border-radius:18px; padding:18px 18px 17px;
        box-shadow: 0 14px 35px rgba(15,23,42,.08), inset 0 1px 0 rgba(255,255,255,.95); min-height:116px;
        backdrop-filter:blur(18px) saturate(145%); transition: transform .28s ease, box-shadow .28s ease, border-color .28s ease;
    }
    .metric-card::before { content:""; position:absolute; top:-30%; left:-45%; width:42%; height:170%; background:linear-gradient(90deg,transparent,rgba(255,255,255,.78),transparent); animation:shimmer 8s ease-in-out infinite; }
    .metric-card:hover { transform:translateY(-7px) rotateX(3deg) rotateY(-2deg); box-shadow:0 22px 48px rgba(37,99,235,.17), inset 0 1px 0 #fff; border-color:rgba(147,197,253,.8); }
    .metric-card:nth-child(2n)::after { content:""; position:absolute; width:70px; height:70px; right:-20px; bottom:-28px; border-radius:50%; background:radial-gradient(circle,rgba(124,58,237,.20),transparent 68%); }
    .metric-label { color: var(--muted); font-size: 0.78rem; font-weight: 650; text-transform: uppercase; letter-spacing: 0.05em; }
    .metric-value { color: var(--navy); font-size: clamp(1.55rem,2vw,2.05rem); font-weight: 780; margin-top: 8px; white-space:nowrap; }
    .metric-note { color: var(--muted); font-size: 0.78rem; margin-top: 2px; }
    [data-testid="stPlotlyChart"] {
        background:linear-gradient(145deg,rgba(255,255,255,.78),rgba(255,255,255,.50));
        border:1px solid rgba(255,255,255,.84); border-radius:22px; padding:7px;
        box-shadow:0 18px 45px rgba(15,23,42,.08),inset 0 1px 0 rgba(255,255,255,.95);
        backdrop-filter:blur(20px) saturate(140%); overflow:hidden; animation:reveal .65s ease both;
        transition:transform .28s ease,box-shadow .28s ease;
    }
    [data-testid="stPlotlyChart"]:hover { transform:translateY(-3px); box-shadow:0 24px 55px rgba(37,99,235,.13),inset 0 1px 0 #fff; }
    [data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,.85); border-radius:18px; overflow:hidden; box-shadow:0 15px 35px rgba(15,23,42,.07); }
    .section-note { background:rgba(239,246,255,.72); border:1px solid rgba(147,197,253,.64); border-radius:14px; padding:14px 16px; color:#1e3a8a; font-size:.88rem; backdrop-filter:blur(16px); }
    .data-note { background:rgba(255,255,255,.66); border:1px solid rgba(255,255,255,.84); border-radius:16px; padding:16px 18px; color:var(--muted); font-size:.88rem; box-shadow:0 12px 30px rgba(15,23,42,.06); backdrop-filter:blur(16px); }
    div[data-baseweb="select"] > div { border-color:rgba(148,163,184,.34); background:rgba(255,255,255,.64); border-radius:12px; backdrop-filter:blur(14px); }
    [data-testid="stSidebar"] [role="radiogroup"] label { padding:9px 11px; border-radius:12px; margin:3px 0; transition:.2s ease; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(219,234,254,.64); transform:translateX(4px); }
    [data-testid="stSidebar"] [data-checked="true"] { background:linear-gradient(120deg,rgba(37,99,235,.13),rgba(124,58,237,.10)); }
    .stButton > button { border-radius: 9px; border: 1px solid var(--line); }
    hr { border-color: var(--line); }
    @media (max-width: 900px) {
        .hero-shell { min-height:0; padding:24px; }
        .hero-ball { width:84px; height:84px; min-width:84px; }
        .metric-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    }
    @media (max-width: 560px) {
        .block-container { padding-left:1rem; padding-right:1rem; }
        .hero-ball { display:none; }
        .metric-grid { grid-template-columns:1fr; }
    }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation:none !important; transition:none !important; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner="Loading player statistics…")
def get_data(path: str) -> pd.DataFrame:
    return load_player_data(path)


def header(kicker: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <section class="hero-shell">
            <div class="hero-copy">
                <div class="page-kicker">{kicker}</div>
                <h1>{title}</h1>
                <p class="page-subtitle">{subtitle}</p>
            </div>
            <div class="hero-ball" aria-hidden="true"></div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def metric_grid(cards: list[tuple[str, str, str]]) -> None:
    markup = ['<section class="metric-grid">']
    for label, value, note in cards:
        markup.append(
            f"""<article class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </article>"""
        )
    markup.append("</section>")
    st.markdown("".join(markup), unsafe_allow_html=True)


def dataframe_view(frame: pd.DataFrame, columns: list[str], height: int = 450) -> None:
    display = frame.loc[:, columns].copy()
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=height,
        column_config={
            "Min": st.column_config.NumberColumn("Minutes", format="%,d"),
            "Goals Per 90": st.column_config.NumberColumn(format="%.2f"),
            "Assists Per 90": st.column_config.NumberColumn(format="%.2f"),
            "Contributions Per 90": st.column_config.NumberColumn(format="%.2f"),
            "Defensive Actions Per 90": st.column_config.NumberColumn(format="%.2f"),
            "Shot Accuracy": st.column_config.ProgressColumn(format="%.1%%", min_value=0, max_value=1),
            "Scouting Score": st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100),
        },
    )


DATA_PATH = str(DEFAULT_DATA_PATH)
try:
    data = get_data(DATA_PATH)
except Exception as exc:
    st.error(f"Unable to load the football dataset: {exc}")
    st.stop()


with st.sidebar:
    st.markdown("### Football analytics")
    st.caption("2025/26 player statistics")
    page = st.radio(
        "View",
        ["Executive overview", "Player performance", "Team and league", "Scouting comparison"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("#### Filters")
    selected_leagues = st.multiselect(
        "League",
        sorted(data["League"].dropna().unique()),
        placeholder="All leagues",
    )
    available_clubs = sorted(
        data.loc[
            data["League"].isin(selected_leagues) if selected_leagues else data.index == data.index,
            "Squad",
        ].dropna().unique()
    )
    selected_clubs = st.multiselect("Club", available_clubs, placeholder="All clubs")
    selected_positions = st.multiselect(
        "Primary position",
        ["Forward", "Midfielder", "Defender", "Goalkeeper"],
        placeholder="All positions",
    )
    st.divider()
    st.caption("Source: supplied Kaggle workbook. Filters apply across the selected view.")


filtered = apply_filters(data, selected_leagues, selected_clubs, selected_positions)
if filtered.empty:
    st.warning("No players match the current filters. Remove one or more filters to continue.")
    st.stop()


if page == "Executive overview":
    header(
        "Executive overview",
        "For You, My All-Rounder",
        "Player and team performance across the top five European leagues in the supplied 2025/26 dataset.",
    )
    metrics = overview_metrics(filtered)
    cards = [
        ("Players", f"{metrics['players']:,}", "Distinct players"),
        ("Goals", f"{metrics['goals']:,}", "Player totals"),
        ("Assists", f"{metrics['assists']:,}", "Player totals"),
        ("Goal contributions", f"{metrics['contributions']:,}", "Goals plus assists"),
        ("Minutes", f"{metrics['minutes'] / 1_000_000:.2f}M", "Recorded minutes"),
        ("Shot accuracy", f"{metrics['shot_accuracy']:.1%}", "Shots on target / shots"),
    ]
    metric_grid(cards)

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        st.plotly_chart(league_goals_assists(filtered), use_container_width=True)
    with right:
        st.plotly_chart(position_contributions(filtered), use_container_width=True)
    st.plotly_chart(top_clubs(filtered), use_container_width=True)

elif page == "Player performance":
    header(
        "Player performance",
        "Attacking output and efficiency",
        "Compare total production with per-90 rates while controlling for meaningful playing time.",
    )
    controls = st.columns([1, 1, 3])
    with controls[0]:
        minimum_minutes = st.slider("Minimum minutes", 0, 2500, 450, 50)
    with controls[1]:
        top_n = st.slider("Players shown", 5, 30, 15, 5)

    qualified = filtered[filtered["Min"] >= minimum_minutes].copy()
    if qualified.empty:
        st.info("No players meet the selected minutes threshold.")
    else:
        left, right = st.columns(2, gap="large")
        with left:
            st.plotly_chart(player_output(qualified, top_n), use_container_width=True)
        with right:
            st.plotly_chart(age_output_scatter(filtered, minimum_minutes), use_container_width=True)
        st.plotly_chart(efficiency_scatter(filtered, minimum_minutes), use_container_width=True)
        st.subheader("Player detail")
        table = qualified.sort_values(
            ["Goal Contributions", "Contributions Per 90"], ascending=False
        )
        dataframe_view(
            table,
            [
                "Player",
                "Squad",
                "League",
                "Position Group",
                "Age",
                "Min",
                "Gls",
                "Ast",
                "Goal Contributions",
                "Goals Per 90",
                "Assists Per 90",
                "Shot Accuracy",
            ],
        )

elif page == "Team and league":
    header(
        "Team and league analysis",
        "Club contribution profiles",
        "Compare attacking output, position mix, available defensive actions and discipline.",
    )
    top_n = st.slider("Clubs shown", 10, 30, 20, 5)
    st.plotly_chart(team_contributions(filtered, top_n), use_container_width=True)
    left, right = st.columns(2, gap="large")
    with left:
        st.plotly_chart(position_club_heatmap(filtered), use_container_width=True)
    with right:
        st.plotly_chart(defensive_by_league(filtered), use_container_width=True)
        st.plotly_chart(discipline_by_league(filtered), use_container_width=True)
    st.markdown(
        '<div class="section-note">Match results, standings, possession, clearances and goals conceded are not present in the supplied player-level dataset, so this view does not infer them.</div>',
        unsafe_allow_html=True,
    )

else:
    header(
        "Scouting comparison",
        "Qualified player profiles",
        "Compare selected outfield players using per-90 output and a transparent project-defined score.",
    )
    minimum_minutes = st.slider("Minimum minutes", 90, 2500, 900, 50)
    scouting = scouting_table(filtered, minimum_minutes)
    if scouting.empty:
        st.info("No outfield players meet the current filters and minutes threshold.")
    else:
        default_players = scouting.head(3)["Player"].tolist()
        selected_names = st.multiselect(
            "Select two to five players",
            scouting["Player"].tolist(),
            default=default_players,
            max_selections=5,
        )
        selected = scouting[scouting["Player"].isin(selected_names)]
        if len(selected) < 2:
            st.info("Select at least two players for a useful comparison.")
        else:
            left, right = st.columns(2, gap="large")
            with left:
                st.plotly_chart(scouting_radar(selected), use_container_width=True)
            with right:
                st.plotly_chart(comparison_bars(selected), use_container_width=True)
            dataframe_view(
                selected.sort_values("Scouting Score", ascending=False),
                [
                    "Player",
                    "Squad",
                    "League",
                    "Position Group",
                    "Age",
                    "Min",
                    "Goals Per 90",
                    "Assists Per 90",
                    "Shot Accuracy",
                    "Defensive Actions Per 90",
                    "Scouting Score",
                ],
                height=260,
            )
        st.markdown(
            '<div class="data-note"><strong>Scouting score:</strong> project-defined percentile score for qualified outfield players. Weights are 45% contributions per 90, 15% shot accuracy, 25% defensive actions per 90 and 15% minutes. It is not an official player rating.</div>',
            unsafe_allow_html=True,
        )

st.caption("For You, My All-Rounder · Source workbook retained in the data folder")

