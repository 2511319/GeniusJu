# dash_app/callbacks.py

import pandas as pd
from dash import Input, Output, State, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from dash_app import create_dash_app  # НЕ из app.py
from services.analysis_service import analyze_data
from services.history_manager import save_history, get_history
from services.crypto_compare_provider import CryptoCompareProvider
from visualization.visualizer import create_chart, prepare_explanations

from flask import request as flask_request
from app import flask_app

dash_app = create_dash_app(flask_app)  # Получаем тот же экземпляр Dash

@dash_app.callback(
    [
        Output('stored-data','data'),
        Output('stored-analysis','data'),
        Output('main-chart','figure'),
        Output('explanations','children'),
    ],
    [
        Input('button-analyze','n_clicks'),
        Input('button-analyze-loaded','n_clicks'),
        Input('checklist-conclusions','value'),
        Input('checklist-basic-indicators','value'),
        Input('checklist-advanced-indicators','value'),
        Input('checklist-technical-analysis','value'),
        Input('checklist-volume','value'),
    ],
    [
        State('input-symbol','value'),
        State('input-interval','value'),
        State('input-num-candles','value'),
        State('stored-data','data'),
        State('stored-analysis','data'),
    ]
)
async def update_output(n1, n2, concl, basic, adv, tech, vol,
                        sym, intrvl, ncand, stored_data, stored_analysis):
    """
    Асинхронный callback FastAPI+Dash, анализирует данные, сохраняет историю,
    формирует график и объяснения.
    """
    triggered = callback_context.triggered[0]['prop_id'].split('.')[0]
    user = flask_request.cookies.get('user_token', 'anonymous')
    selected = concl + basic + adv + tech + vol

    if triggered == 'button-analyze' and n1:
        # Шаг 1: анализ через OpenAI и CryptoCompare
        result = await analyze_data(user, sym, intrvl, int(ncand))
        if 'error' in result:
            return dash_app.no_update, dash_app.no_update, dash_app.no_update, [html.Div(result['error'])]
        df = await CryptoCompareProvider().fetch_ohlcv(sym, intrvl, int(ncand))
        save_history(user, sym, intrvl, result)
        fig = create_chart(selected, df, result)
        expl = prepare_explanations(selected, result)
        children = [html.H5(e['Название']) for e in expl] + [dcc.Markdown(e['Текст']) for e in expl]
        return df.to_dict('records'), result, fig, children

    if triggered == 'button-analyze-loaded' and n2:
        history = get_history(user)
        if not history:
            return dash_app.no_update, dash_app.no_update, dash_app.no_update, [html.Div("История пуста.")]
        last = history[-1]
        df = await CryptoCompareProvider().fetch_ohlcv(last['symbol'], last['interval'], int(ncand))
        fig = create_chart(selected, df, last['result'])
        expl = prepare_explanations(selected, last['result'])
        children = [html.H5(e['Название']) for e in expl] + [dcc.Markdown(e['Текст']) for e in expl]
        return df.to_dict('records'), last['result'], fig, children

    # Обновление графика при переключении чеклистов
    checklist_ids = {
        'checklist-conclusions','checklist-basic-indicators',
        'checklist-advanced-indicators','checklist-technical-analysis',
        'checklist-volume'
    }
    if triggered in checklist_ids and stored_data and stored_analysis:
        df = pd.DataFrame(stored_data)
        fig = create_chart(selected, df, stored_analysis)
        expl = prepare_explanations(selected, stored_analysis)
        children = [html.H5(e['Название']) for e in expl] + [dcc.Markdown(e['Текст']) for e in expl]
        return stored_data, stored_analysis, fig, children

    raise PreventUpdate
