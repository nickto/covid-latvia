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
            dbc.CardHeader("Deaths"),
            dbc.CardBody(id=ID_PREFIX + "-deaths"),
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
        layout=go.Layout(
            title="Cases and deaths",
            yaxis=dict(title="Cases"),
            yaxis2=dict(title="Deaths", overlaying="y", side="right"),
        ),
    )

    fig.update_xaxes(rangeslider_visible=True, showspikes=True)
    fig.update_yaxes(showspikes=True, rangemode="tozero")

    fig.layout.margin = go.layout.Margin(t=0, b=0, l=0, r=0)

    return dcc.Graph(figure=fig,
                     config={
                         "displaylogo": False,
                         "displayModeBar": False,
                         "modeBarButtonsToRemove": [
                             "toggleSpikelines",
                             "autoScale2d"
                         ],
                     },
                     id=ID_PREFIX + "-cases-and-deaths-graph")


@app.callback(Output(ID_PREFIX + "-cases-and-deaths-graph", "figure"),
              Input(ID_PREFIX + "-cases-and-deaths-graph", "relayoutData"),
              State(ID_PREFIX + "-cases-and-deaths-graph", "figure"))
def update_yaxis_range(xaxis_range, fig):
    if fig is None or xaxis_range is None or "xaxis.range" not in xaxis_range:
        return dash.no_update

    # Get new range
    begin, end = xaxis_range["xaxis.range"]

    # Find max y in the new range
    data = zip(fig["data"][0]["x"], fig["data"][0]["y"])
    y_max1 = max([y for x, y in data if x >= begin and x <= end])

    data = zip(fig["data"][1]["x"], fig["data"][1]["y"])
    y_max2 = max([y for x, y in data if x >= begin and x <= end])

    logging.warning(y_max1)
    logging.warning(y_max2)

    # Make sure range slider does not change range
    for i, yaxis in enumerate(["yaxis", "yaxis2"]):
        fig["layout"]["xaxis"]["rangeslider"][yaxis]["range"] = [
            min(fig["data"][i]["y"]) - 0.05 * max(fig["data"][i]["y"]),
            1.05 * max(fig["data"][i]["y"]),
        ]
        fig["layout"]["xaxis"]["rangeslider"][yaxis]["rangemode"] = "normal"

    # Change range of graph
    fig["layout"]["yaxis"]["range"][1] = 1.05 * y_max1
    fig["layout"]["yaxis"]["autorange"] = False

    fig["layout"]["yaxis2"]["range"][1] = 1.05 * y_max2
    fig["layout"]["yaxis2"]["autorange"] = False

    logging.warning(fig["layout"].keys())

    return fig