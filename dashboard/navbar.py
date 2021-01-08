from typing import Container
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output


def _gen_nav_time(name, href, active):
    if active is None:
        is_active = False
    else:
        is_active = name == active

    if is_active:
        return dbc.NavItem(dbc.NavLink(name, href=href, className="active"))
    else:
        return dbc.NavItem(dbc.NavLink(name, href=href))

def gen_layout(active=None):
    # yapf: disable
    return dbc.Navbar(
        [
            dbc.Nav(dbc.NavbarBrand("COVID-19 Latvia", href="/"), navbar=True),
            dbc.Nav([
                _gen_nav_time("Overview", "/overview", active),
                _gen_nav_time("Daily", "/daily", active),
            ], horizontal="end", navbar=True),
        ],
    )
    # yapf: enable