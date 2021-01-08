import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from dashboard import overview
from dashboard import daily

server = app.server

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    # 2f33271e16
    html.Div(id="page-content")
])


@app.callback(Output("page-content", "children"),
              Input("url", "pathname"))
def display_page(pathname):
    if pathname in ("/", "/overview"):
        return overview.layout
    elif pathname in ("/daily"):
        return daily.layout
    else:
        return "404"

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port="8051", threaded=True)