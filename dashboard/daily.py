import logging
import dash
from dash_bootstrap_components._components.CardBody import CardBody
from dash_bootstrap_components._components.CardHeader import CardHeader
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dashboard import app_data
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from app import app

from dashboard import navbar
from dashboard import plots

ID_PREFIX = "daily"

# yapf: disable
layout = dbc.Container([
    navbar.gen_layout(active="Daily"),
    dbc.Container([
        html.H1("Daily"),
        dbc.Card([
            dbc.CardHeader("Cases and deaths"),
            dbc.CardBody(id=ID_PREFIX + "-cases-and-deaths"),
        ], style={"margin-top": "1ex"}),
        dbc.Card([
            dbc.CardHeader("Positivity rate"),
            dbc.CardBody(id=ID_PREFIX + "-positivity-rate"),
        ], style={"margin-top": "1ex"}),
        dbc.Card([
            dbc.CardHeader("Tests"),
            dbc.CardBody(id=ID_PREFIX + "-tests"),
        ], style={"margin-top": "1ex"}),

    ])
], id=ID_PREFIX + "-container")
# yapf: enable

plots.gen_2_cols_plot_from_cases_callbacks(
    x="date",
    y1="cases",
    y2="deaths",
    y1_name="Cases",
    y2_name="Deaths",
    initial_trigger_id=ID_PREFIX + "-container",
    parent_id=ID_PREFIX + "-cases-and-deaths",
    app=app,
    hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>")

plots.gen_col_plot_from_cases_callbacks(
    x="date",
    y="positivity_rate",
    initial_trigger_id=ID_PREFIX + "-container",
    parent_id=ID_PREFIX + "-positivity-rate",
    app=app)

plots.gen_col_plot_from_cases_callbacks(
    x="date",
    y="tests",
    initial_trigger_id=ID_PREFIX + "-container",
    parent_id=ID_PREFIX + "-tests",
    hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
    app=app)