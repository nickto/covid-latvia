import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app

from dashboard import navbar

layout = html.Div([
    navbar.gen_layout(active="Daily"),
])
