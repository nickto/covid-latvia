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
        ]),
        dbc.Card([
            dbc.CardHeader("Positivity rate"),
            dbc.CardBody(id=ID_PREFIX + "-positivity-rate"),
        ]),
        dbc.Card([
            dbc.CardHeader("Tests"),
            dbc.CardBody(id=ID_PREFIX + "-tests"),
        ]),

    ])
], id=ID_PREFIX + "-container")
# yapf: enable


@app.callback(Output(ID_PREFIX + "-cases-and-deaths", "children"),
              Input(ID_PREFIX + "-container", "children"))
def foo(_):
    cases = app_data.read_cases()

    fig = go.Figure(
        data=[
            go.Scatter(
                x=pd.to_datetime(cases["date"]),
                y=cases["cases"],
                name="Cases",
                yaxis="y1",
                hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
            ),
            go.Scatter(
                x=pd.to_datetime(cases["date"]),
                y=cases["deaths"],
                name="Deaths",
                yaxis="y2",
                hovertemplate="<b>%{x}</b><br>%{y:,.0f}<extra></extra>",
            ),
        ],
        layout=go.Layout(title="Cases and deaths",
                         yaxis=dict(title="Cases"),
                         yaxis2=dict(title="Deaths",
                                     overlaying="y",
                                     side="right"),
                         legend=dict(x=0, y=1)),
    )

    fig.update_xaxes(rangeslider_visible=True, showspikes=True)
    fig.update_yaxes(showspikes=True, rangemode="tozero")

    fig.layout.margin = go.layout.Margin(t=0, b=0, l=0, r=0)

    return dcc.Graph(figure=fig,
                     config={
                         "displaylogo":
                         False,
                         "displayModeBar":
                         False,
                         "modeBarButtonsToRemove":
                         ["toggleSpikelines", "autoScale2d"],
                     },
                     id=ID_PREFIX + "-cases-and-deaths-graph")


@app.callback(Output(ID_PREFIX + "-cases-and-deaths-graph", "figure"),
              Input(ID_PREFIX + "-cases-and-deaths-graph", "relayoutData"),
              State(ID_PREFIX + "-cases-and-deaths-graph", "figure"))
def update_yaxis_range(xaxis_range, fig):
    return plots.update_double_yaxis_range(xaxis_range, fig)


@app.callback(Output(ID_PREFIX + "-positivity-rate", "children"),
              Input(ID_PREFIX + "-container", "children"))
def foo(_):
    cases = app_data.read_cases()

    fig = go.Figure(data=[
        go.Scatter(
            x=pd.to_datetime(cases["date"]),
            y=cases["positivity_rate"],
            name="Cases",
            hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>",
        ),
    ], )

    fig.update_xaxes(rangeslider_visible=True, showspikes=True)
    fig.update_yaxes(showspikes=True)

    fig.layout.margin = go.layout.Margin(t=0, b=0, l=0, r=0)

    return dcc.Graph(figure=fig,
                     config={
                         "displaylogo":
                         False,
                         "displayModeBar":
                         False,
                         "modeBarButtonsToRemove":
                         ["toggleSpikelines", "autoScale2d"],
                     },
                     id=ID_PREFIX + "-cases-and-deaths-graph")
