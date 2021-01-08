import datetime
import dash
import logging
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from app import app

from dashboard import navbar
from dashboard import app_data
from dashboard import plots

ID_PREFIX = "overview"

# yapf: disable
layout = dbc.Container([
    navbar.gen_layout(active="Overview"),
    dbc.Container([
        html.H1("Overview"),
        html.Div([
            html.H2("Data freshness"),
            html.Table(html.Tbody([
                html.Tr([
                    html.Td("Last date in the data:"),
                    html.Td(id=ID_PREFIX + "-data-last-date", style={"padding-left": "1em"})
                ]),
                html.Tr([
                    html.Td("Last updated on:"),
                    html.Td(id=ID_PREFIX + "-data-last-date-updated", style={"padding-left": "1em"})
                ]),
            ]), id=ID_PREFIX + "-last-date-table")
        ]),
        html.Div([
            html.H2("Summary"),
            html.Div(id=ID_PREFIX + "-summary-container")
        ]),
        html.Div(id=ID_PREFIX + "14day-plot-container"),
    ]),
], id=ID_PREFIX + "-container")
# yapf: enable


@app.callback(Output(ID_PREFIX + "-data-last-date-updated", "children"),
              Output(ID_PREFIX + "-data-last-date", "children"),
              Input(ID_PREFIX + "-last-date-table", "children"))
def update_last_dates(_):
    cases = app_data.read_cases()
    cases_meta = app_data.read_cases_meta()

    last_data = max(cases["date"])
    last_data = pd.to_datetime(last_data)
    last_data = last_data.strftime("%Y-%m-%d")

    last_updated = pd.to_datetime(
        cases_meta["last_modified"]).strftime("%Y-%m-%d %H:%M")

    return last_updated, last_data


def _get_direction(current, past, lower_is_better=True):
    if current > past:
        if lower_is_better:
            return html.I(className="fas fa-arrow-up",
                          style={"color": "DarkRed"})
        else:
            return html.I(className="fas fa-arrow-up",
                          style={"color": "DarkGreen"})
    elif current < past:
        if lower_is_better:
            return html.I(className="fas fa-arrow-down",
                          style={"color": "DarkGreen"})
        else:
            return html.I(className="fas fa-arrow-down",
                          style={"color": "DarkRed"})
    else:
        return html.I(className="fas fa-arrow-right",
                      style={"color": "DarkOrange"})


def _get_summary(df, col, display_name):
    value = df.loc[:, col].iloc[-1]

    if value > 1:
        value_fmtd = f"{value:,.1f}"
    else:
        value_fmtd = f"{value:,.3f}"

    # Compare to 1 day ago
    if col in ("tests"):
        direction_1d = _get_direction(value, df.loc[:, col].iloc[-2], False)
    else:
        direction_1d = _get_direction(value, df.loc[:, col].iloc[-2])

    # Compare to 7 days ago
    if col in ("tests"):
        direction_7d = _get_direction(value, df.loc[:, col].iloc[-8], False)
    else:
        direction_7d = _get_direction(value, df.loc[:, col].iloc[-8])

    return html.Tr([
        html.Td(display_name),
        html.Td(value_fmtd, style={"text-align": "right", "padding-left": "1em"}),
        html.Td(direction_1d, style={"text-align": "center"}),
        html.Td(direction_7d, style={"text-align": "center"})
    ])


@app.callback(Output(ID_PREFIX + "-summary-container", "children"),
              Input(ID_PREFIX + "-container", "children"))
def update_summary_table(_):
    cases = app_data.read_cases()

    rows = []

    rows.append(
        _get_summary(cases, "cases_14_days_sum_per_100K", "14-day incidence"))

    rows.append(_get_summary(cases, "cases", "Daily cases"))

    rows.append(_get_summary(cases, "positivity_rate", "Positivity rate"))

    rows.append(_get_summary(cases, "tests", "Tests"))

    return html.Table([
        html.Thead(
            html.Tr([
                html.Td(),
                html.Td(style={"padding-left": "1em"}),
                html.Td("Since yesterday", style={"padding-left": "1em"}),
                html.Td("Since last week", style={"padding-left": "1em"}),
            ])),
        html.Tbody(rows),
    ])


@app.callback(Output(ID_PREFIX + "14day-plot-container", "children"),
              Input(ID_PREFIX + "-container", "children"))
def render_14_day_plot(_):
    col = "cases_14_days_sum_per_100K"
    cases = app_data.read_cases()
    fig = go.Figure(data=[
        go.Scatter(x=pd.to_datetime(cases["date"]),
                   y=cases[col],
                   hovertemplate="<b>%{x}</b><br>%{y:.1f}<extra></extra>"),
    ])

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_yaxes(rangemode="tozero")

    last_date = pd.to_datetime(cases.loc[:, "date"]).max()
    last_date = last_date.date()
    initial_range = (
        last_date - datetime.timedelta(days=90),
        last_date,
    )
    fig.layout.xaxis.update(
        range=initial_range,
        showspikes=True,
    )

    fig.layout.yaxis.update(showspikes=True)
    fig.layout.margin = go.layout.Margin(t=0, b=0, l=0, r=0)

    layout = dbc.Card([
        dbc.CardHeader("14-day cumulative cases per 100,000 inhabitants"),
        dbc.CardBody(
            dcc.Graph(figure=fig,
                      config={
                          "displaylogo": False,
                          "displayModeBar": False,
                      },
                      id=ID_PREFIX + "-cases-graph")),
    ], style={"margin-top": "1ex"})

    return layout


@app.callback(Output(ID_PREFIX + "-cases-graph", "figure"),
              Input(ID_PREFIX + "-cases-graph", "relayoutData"),
              State(ID_PREFIX + "-cases-graph", "figure"))
def update_yaxis_range(xaxis_range, fig):
    return plots._update_yaxis_range(xaxis_range, fig)
