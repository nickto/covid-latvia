import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_html_components.Thead import Thead
import pandas as pd
import yaml

from app import app

from dashboard import navbar
from dashboard import app_data

ID_PREFIX = "overview"

# yapf: disable
layout = html.Div([
    navbar.gen_layout(),
    html.Div([
        html.H1("Overview"),
        html.Div([
            html.Table(html.Tbody([
                html.Tr([
                    html.Td("Last date in the data:"),
                    html.Td(id=ID_PREFIX + "-data-last-date")
                ]),
                html.Tr([
                    html.Td("Last updated on:"),
                    html.Td(id=ID_PREFIX + "-data-last-date-updated")
                ]),
            ]), id=ID_PREFIX + "-last-date-table")
        ]),
        html.Div([
            html.H2("Summary"),
            html.Div(id=ID_PREFIX + "-summary-container")
        ], id=ID_PREFIX + "-summary-section"),
    ]),

])
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
            return html.I(className="fas fa-arrow-up", style={"color": "DarkRed"})
        else:
            return html.I(className="fas fa-arrow-up", style={"color": "DarkGreen"})
    elif current < past:
        if lower_is_better:
            return html.I(className="fas fa-arrow-down", style={"color": "DarkGreen"})
        else:
            return html.I(className="fas fa-arrow-down", style={"color": "DarkRed"})
    else:
        return html.I(className="fas fa-arrow-right", style={"color": "DarkOrange"})


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
        html.Td(value_fmtd),
        html.Td(direction_1d),
        html.Td(direction_7d)
    ])


@app.callback(Output(ID_PREFIX + "-summary-container", "children"),
              Input(ID_PREFIX + "-summary-section", "children"))
def update_summary_table(_):
    cases = app_data.read_cases()

    rows = []

    rows.append(
        _get_summary(cases, "cases_14_days_sum_per_100K", "14-day incidence"))

    rows.append(_get_summary(cases, "cases", "Daily cases"))

    rows.append(_get_summary(cases, "positivity_rate", "Positivity rate"))

    rows.append(_get_summary(cases, "tests", "Tests"))

    return html.Table([
        html.Thead(html.Tr([
            html.Td(),
            html.Td(),
            html.Td("Since yesterday"),
            html.Td("Since last week"),
        ])),
        html.Tbody(rows),
    ])
