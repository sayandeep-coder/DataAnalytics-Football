from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLORS = {
    "navy": "#14213D",
    "blue": "#2563EB",
    "sky": "#60A5FA",
    "green": "#059669",
    "amber": "#D97706",
    "red": "#DC2626",
    "slate": "#64748B",
    "grid": "#E2E8F0",
}

LEAGUE_COLORS = {
    "Premier League": "#3B2A80",
    "La Liga": "#E11D48",
    "Bundesliga": "#D97706",
    "Serie A": "#2563EB",
    "Ligue 1": "#059669",
}


def style_figure(fig: go.Figure, height: int = 390) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=28, r=28, t=86, b=36),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=COLORS["navy"]),
        title=dict(font=dict(size=18, color=COLORS["navy"]), x=0.025, y=0.965, xanchor="left", yanchor="top"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=0.99,
            title_text="",
            bgcolor="rgba(255,255,255,0)",
        ),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Inter, Segoe UI"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"], zeroline=False, linecolor=COLORS["grid"])
    return fig


def league_goals_assists(frame: pd.DataFrame) -> go.Figure:
    league = (
        frame.groupby("League", as_index=False)[["Gls", "Ast"]]
        .sum()
        .rename(columns={"Gls": "Goals", "Ast": "Assists"})
    )
    long = league.melt("League", var_name="Metric", value_name="Total")
    fig = px.bar(
        long,
        x="League",
        y="Total",
        color="Metric",
        barmode="group",
        text_auto=",.0f",
        color_discrete_map={"Goals": COLORS["blue"], "Assists": COLORS["sky"]},
        title="Goals and assists by league",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig)


def position_contributions(frame: pd.DataFrame) -> go.Figure:
    position = (
        frame.groupby("Position Group", as_index=False)["Goal Contributions"]
        .sum()
        .sort_values("Goal Contributions", ascending=False)
    )
    fig = px.pie(
        position,
        names="Position Group",
        values="Goal Contributions",
        hole=0.62,
        title="Goal contributions by position",
        color="Position Group",
        color_discrete_map={
            "Forward": COLORS["blue"],
            "Midfielder": COLORS["green"],
            "Defender": COLORS["amber"],
            "Goalkeeper": COLORS["slate"],
        },
    )
    fig.update_traces(textinfo="percent+label", hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>")
    fig = style_figure(fig, height=420)
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.04,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0)",
        ),
        margin=dict(l=24, r=24, t=84, b=68),
    )
    return fig


def top_clubs(frame: pd.DataFrame, n: int = 10) -> go.Figure:
    clubs = (
        frame.groupby(["Squad", "League"], as_index=False)["Goal Contributions"]
        .sum()
        .nlargest(n, "Goal Contributions")
        .sort_values("Goal Contributions")
    )
    fig = px.bar(
        clubs,
        x="Goal Contributions",
        y="Squad",
        orientation="h",
        color="League",
        color_discrete_map=LEAGUE_COLORS,
        text_auto=",.0f",
        title=f"Top {n} clubs by player goal contributions",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig, height=430)


def player_output(frame: pd.DataFrame, n: int = 15) -> go.Figure:
    leaders = frame.nlargest(n, "Goal Contributions").sort_values("Goal Contributions")
    fig = go.Figure()
    fig.add_bar(
        name="Goals",
        x=leaders["Gls"],
        y=leaders["Player"],
        orientation="h",
        marker_color=COLORS["blue"],
        hovertemplate="%{y}<br>Goals: %{x}<extra></extra>",
    )
    fig.add_bar(
        name="Assists",
        x=leaders["Ast"],
        y=leaders["Player"],
        orientation="h",
        marker_color=COLORS["sky"],
        hovertemplate="%{y}<br>Assists: %{x}<extra></extra>",
    )
    fig.update_layout(barmode="stack", title=f"Top {n} attacking contributors")
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig, height=510)


def age_output_scatter(frame: pd.DataFrame, minimum_minutes: int) -> go.Figure:
    qualified = frame[frame["Min"] >= minimum_minutes].copy()
    fig = px.scatter(
        qualified,
        x="Age",
        y="Goal Contributions",
        size="Min",
        color="League",
        color_discrete_map=LEAGUE_COLORS,
        hover_name="Player",
        hover_data={"Squad": True, "Min": ":,.0f", "Age": ".0f"},
        title=f"Age and attacking output ({minimum_minutes:,}+ minutes)",
        size_max=26,
    )
    fig.update_xaxes(title="Age")
    fig.update_yaxes(title="Goal contributions")
    return style_figure(fig, height=510)


def efficiency_scatter(frame: pd.DataFrame, minimum_minutes: int) -> go.Figure:
    qualified = frame[frame["Min"] >= minimum_minutes].copy()
    fig = px.scatter(
        qualified,
        x="Goals Per 90",
        y="Assists Per 90",
        size="Min",
        color="Position Group",
        hover_name="Player",
        hover_data={"Squad": True, "League": True, "Min": ":,.0f"},
        title=f"Per-90 attacking efficiency ({minimum_minutes:,}+ minutes)",
        size_max=25,
        color_discrete_sequence=[COLORS["blue"], COLORS["green"], COLORS["amber"], COLORS["slate"]],
    )
    return style_figure(fig, height=470)


def team_contributions(frame: pd.DataFrame, n: int = 20) -> go.Figure:
    team = (
        frame.groupby(["Squad", "League"], as_index=False)[["Gls", "Ast"]]
        .sum()
    )
    team["Goal Contributions"] = team["Gls"] + team["Ast"]
    team = team.nlargest(n, "Goal Contributions").sort_values("Goal Contributions")
    fig = px.bar(
        team,
        x="Goal Contributions",
        y="Squad",
        color="League",
        orientation="h",
        color_discrete_map=LEAGUE_COLORS,
        text_auto=",.0f",
        title=f"Top {n} clubs by attacking contribution",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig, height=610)


def position_club_heatmap(frame: pd.DataFrame, n: int = 12) -> go.Figure:
    leading_clubs = (
        frame.groupby("Squad")["Goal Contributions"].sum().nlargest(n).index
    )
    matrix = (
        frame[frame["Squad"].isin(leading_clubs)]
        .pivot_table(
            index="Squad",
            columns="Position Group",
            values="Goal Contributions",
            aggfunc="sum",
            fill_value=0,
        )
        .reindex(leading_clubs)
    )
    fig = px.imshow(
        matrix,
        text_auto=".0f",
        aspect="auto",
        color_continuous_scale=[[0, "#EFF6FF"], [1, COLORS["blue"]]],
        title=f"Position contribution for leading {n} clubs",
        labels=dict(color="Contributions"),
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig, height=520)


def defensive_by_league(frame: pd.DataFrame) -> go.Figure:
    defensive = (
        frame.groupby("League", as_index=False)[["TklW", "Int"]]
        .sum()
        .rename(columns={"TklW": "Tackles won", "Int": "Interceptions"})
    )
    long = defensive.melt("League", var_name="Metric", value_name="Total")
    fig = px.bar(
        long,
        x="League",
        y="Total",
        color="Metric",
        barmode="group",
        color_discrete_map={"Tackles won": COLORS["green"], "Interceptions": COLORS["amber"]},
        title="Available defensive actions by league",
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig)


def discipline_by_league(frame: pd.DataFrame) -> go.Figure:
    discipline = (
        frame.groupby("League", as_index=False)[["CrdY", "CrdR"]]
        .sum()
        .rename(columns={"CrdY": "Yellow cards", "CrdR": "Red cards"})
    )
    long = discipline.melt("League", var_name="Card", value_name="Total")
    fig = px.bar(
        long,
        x="League",
        y="Total",
        color="Card",
        barmode="group",
        color_discrete_map={"Yellow cards": "#EAB308", "Red cards": COLORS["red"]},
        title="Discipline by league",
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig)


def scouting_radar(selected: pd.DataFrame) -> go.Figure:
    metrics = [
        "Goals Per 90",
        "Assists Per 90",
        "Shot Accuracy",
        "Defensive Actions Per 90",
        "Scouting Score",
    ]
    labels = ["Goals / 90", "Assists / 90", "Shot accuracy", "Defensive / 90", "Scouting score"]
    normalized = selected[metrics].copy()
    for metric in metrics[:-1]:
        maximum = max(float(normalized[metric].max()), 0.0001)
        normalized[metric] = normalized[metric] / maximum * 100

    fig = go.Figure()
    palette = [COLORS["blue"], COLORS["green"], COLORS["amber"], COLORS["red"], COLORS["slate"]]
    for color, (index, row) in zip(palette, normalized.iterrows()):
        original = selected.loc[index]
        fig.add_trace(
            go.Scatterpolar(
                r=row[metrics].tolist() + [row[metrics[0]]],
                theta=labels + [labels[0]],
                fill="toself",
                opacity=0.42,
                name=original["Player"],
                line=dict(color=color, width=2),
            )
        )
    fig.update_layout(
        title="Selected-player profile",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%", gridcolor=COLORS["grid"]),
            angularaxis=dict(gridcolor=COLORS["grid"]),
        ),
    )
    return style_figure(fig, height=520)


def comparison_bars(selected: pd.DataFrame) -> go.Figure:
    long = selected.melt(
        id_vars="Player",
        value_vars=["Goals Per 90", "Assists Per 90", "Defensive Actions Per 90"],
        var_name="Metric",
        value_name="Per 90",
    )
    fig = px.bar(
        long,
        x="Metric",
        y="Per 90",
        color="Player",
        barmode="group",
        title="Per-90 comparison",
    )
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return style_figure(fig, height=520)

