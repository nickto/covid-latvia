import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

def gen_layout():
    return dbc.Nav(
        [
            dbc.NavbarBrand("COVID-19 Latvia", href="/"),
            dbc.NavLink("Overview", href="/overview"),
            dbc.NavLink("Daily", href="/daily"),
        ]
    )