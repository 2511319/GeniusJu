# dash_app/__init__.py

import dash
import dash_bootstrap_components as dbc
# from dash.long_callback import DiskcacheLongCallbackManager # Не здесь, а в app.py

# def create_dash_app(flask_app): # Старая
def create_dash_app(flask_app, long_callback_manager=None): # Новая
    """
    Создаёт Dash-приложение поверх переданного Flask-сервера.
    """
    dash_app = dash.Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/', # Убедитесь, что этот параметр используется
        external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], # или ваши текущие стили
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
        suppress_callback_exceptions=True,
        long_callback_manager=long_callback_manager
    )
    dash_app.title = "ChartGenius2"
    # Загрузка layout и callbacks из отдельных файлов
    from .layout import layout # .layout т.к. layout.py в той же директории
    from . import callbacks # .callbacks для импорта callbacks.py из текущего пакета
    dash_app.layout = layout
    return dash_app
