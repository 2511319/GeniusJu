# dash_app/__init__.py

import dash
import dash_bootstrap_components as dbc
from dash_app.layout import layout

def create_dash_app(server):
    """
    Создаёт Dash-приложение поверх переданного Flask-сервера.
    """
    dash_app = dash.Dash(
        __name__,
        server=server,
        requests_pathname_prefix="/",
        routes_pathname_prefix="/",
        external_stylesheets=[dbc.themes.DARKLY],
        suppress_callback_exceptions=True
    )
    dash_app.title = "ChartGenius2"
    dash_app.layout = layout
    return dash_app
