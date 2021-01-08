import dash
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd

from dashboard import app_data


def _update_yaxis_range(xaxis_range, fig):
    if fig is None or xaxis_range is None or "xaxis.range" not in xaxis_range:
        return dash.no_update

    # Get new range
    begin, end = xaxis_range["xaxis.range"]

    # Find max y in the new range
    data = zip(fig["data"][0]["x"], fig["data"][0]["y"])
    y_max = max([y for x, y in data if x >= begin and x <= end])

    # Make sure range slider does not change range
    fig["layout"]["xaxis"]["rangeslider"]["yaxis"]["range"] = [
        min(fig["data"][0]["y"]) - 0.05 * max(fig["data"][0]["y"]),
        1.05 * max(fig["data"][0]["y"]),
    ]
    fig["layout"]["xaxis"]["rangeslider"]["yaxis"]["rangemode"] = "normal"

    # Change range of graph
    fig["layout"]["yaxis"]["range"][0] = 0 - 0.05 * y_max
    fig["layout"]["yaxis"]["range"][1] = 1.05 * y_max
    fig["layout"]["yaxis"]["autorange"] = False
    return fig


def gen_col_plot_from_cases_callbacks(
        x,
        y,
        initial_trigger_id,
        parent_id,
        app,
        hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>"):
    """
    Args:
        x: x col name (should be date).
        y: y col name.
        initial_trigger_id: component ID that triggers initial rendering.
        parent_id: component ID of the parent element.
        app: dash.Dash instance.
    """
    def _reder_plot(_):
        cases = app_data.read_cases()

        fig = go.Figure(data=[
            go.Scatter(
                x=pd.to_datetime(cases[x]),
                y=cases[y],
                hovertemplate=hovertemplate,
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
                         id=f"{parent_id:s}-graph")

    return (
        app.callback(
            Output(parent_id, "children"),
            Input(initial_trigger_id, "children"),
        )(_reder_plot),
        app.callback(
            Output(f"{parent_id:s}-graph", "figure"),
            Input(f"{parent_id:s}-graph", "relayoutData"),
            State(f"{parent_id:s}-graph", "figure"),
        )(_update_yaxis_range),
    )


def _update_double_yaxis_range(xaxis_range, fig):
    if fig is None or xaxis_range is None or "xaxis.range" not in xaxis_range:
        return dash.no_update

    # Get new range
    begin, end = xaxis_range["xaxis.range"]

    # Find max y in the new range
    data = zip(fig["data"][0]["x"], fig["data"][0]["y"])
    y_max1 = max([y for x, y in data if x >= begin and x <= end])

    data = zip(fig["data"][1]["x"], fig["data"][1]["y"])
    y_max2 = max([y for x, y in data if x >= begin and x <= end])

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

    return fig


def gen_2_cols_plot_from_cases_callbacks(
        x,
        y1,
        y2,
        y1_name,
        y2_name,
        initial_trigger_id,
        parent_id,
        app,
        hovertemplate="<b>%{x}</b><br>%{y:,.2f}<extra></extra>"):
    """
    Args:
        x: x col name (should be date).
        y1: y col name.
        y2: the other y col name.
        y1_name: y col display name.
        y2_name: the other y col display name.
        initial_trigger_id: component ID that triggers initial rendering.
        parent_id: component ID of the parent element.
        app: dash.Dash instance.
    """
    cases = app_data.read_cases()

    def _reder_plot(_):
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=pd.to_datetime(cases[x]),
                    y=cases[y1],
                    name=y1_name,
                    yaxis="y1",
                    hovertemplate=hovertemplate,
                ),
                go.Scatter(
                    x=pd.to_datetime(cases[x]),
                    y=cases[y2],
                    name=y2_name,
                    yaxis="y2",
                    hovertemplate=hovertemplate,
                ),
            ],
            layout=go.Layout(
                yaxis=dict(title=y1_name),
                yaxis2=dict(title=y2_name, overlaying="y", side="right"),
                legend=dict(x=0, y=1),
            ),
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
                         id=f"{parent_id}-graph")

    return (
        app.callback(
            Output(parent_id, "children"),
            Input(initial_trigger_id, "children"),
        )(_reder_plot),
        app.callback(
            Output(f"{parent_id:s}-graph", "figure"),
            Input(f"{parent_id:s}-graph", "relayoutData"),
            State(f"{parent_id:s}-graph", "figure"),
        )(_update_double_yaxis_range),
    )
