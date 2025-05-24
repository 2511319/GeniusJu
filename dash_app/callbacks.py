# dash_app/callbacks.py

import pandas as pd
import dash
import dash_bootstrap_components as dbc
# Ensure all necessary Dash components are imported
from dash import Input, Output, State, callback_context, dcc, html, ClientsideFunction, no_update, PreventUpdate
from services import preset_manager # Import preset_manager

from dash_app import create_dash_app
from services.analysis_service import analyze_data
from services.history_manager import save_history, get_history
from services.crypto_compare_provider import CryptoCompareProvider
from visualization.visualizer import create_chart, prepare_explanations
from dash_app.layout import DEFAULT_SYMBOL, DEFAULT_INTERVAL, DEFAULT_CANDLES

from flask import request as flask_request
from app import flask_app
from config import logger

dash_app = create_dash_app(flask_app)

# Theme Callbacks (existing)
FLATLY_URL = dbc.themes.FLATLY
DARKLY_URL = dbc.themes.DARKLY
dash_app.clientside_callback(
    ClientsideFunction(namespace='clientside', function_name='update_theme'),
    Output('theme-link', 'href'),
    Output('theme-store', 'data'),
    Output('theme-switch', 'value', allow_duplicate=True),
    Input('theme-switch', 'value'),
    Input('theme-store', 'data'),
    custom_data={'FLATLY_URL': FLATLY_URL, 'DARKLY_URL': DARKLY_URL},
    prevent_initial_call=False
)

STYLE_SHOW = {'display': 'block', 'padding-top': '10px', 'border-top': '1px solid #eee', 'margin-top': '10px'}
STYLE_HIDE = {'display': 'none'}
@dash_app.callback(
    [Output("settings-RSI-params", "style"), Output("settings-MACD-params", "style"),
     Output("settings-Stochastic_Oscillator-params", "style"), Output("settings-ATR-params", "style")],
    [Input("checklist-basic-indicators", "value")], prevent_initial_call=True
)
def toggle_basic_indicator_settings(selected_indicators):
    selected_indicators = selected_indicators or []
    return (STYLE_SHOW if "RSI" in selected_indicators else STYLE_HIDE,
            STYLE_SHOW if "MACD" in selected_indicators else STYLE_HIDE,
            STYLE_SHOW if "Stochastic_Oscillator" in selected_indicators else STYLE_HIDE,
            STYLE_SHOW if "ATR" in selected_indicators else STYLE_HIDE)

@dash_app.callback(
    [Output("settings-Bollinger_Bands-params", "style"), Output("settings-Ichimoku_Cloud-params", "style")],
    [Input("checklist-advanced-indicators", "value")], prevent_initial_call=True
)
def toggle_advanced_indicator_settings(selected_indicators):
    selected_indicators = selected_indicators or []
    return (STYLE_SHOW if "Bollinger_Bands" in selected_indicators else STYLE_HIDE,
            STYLE_SHOW if "Ichimoku_Cloud" in selected_indicators else STYLE_HIDE)

# Preset Management Callbacks
@dash_app.callback(
    Output('modal-save-preset', 'is_open'),
    [Input('button-open-save-modal', 'n_clicks'),
     Input('button-cancel-save-preset', 'n_clicks'),
     Input('button-confirm-save-preset', 'n_clicks_timestamp')],
    [State('modal-save-preset', 'is_open'),
     State('save-preset-feedback', 'children')],
    prevent_initial_call=True
)
def toggle_save_preset_modal(n_open, n_cancel, ts_confirm_save, is_open, save_feedback_children):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'button-open-save-modal' and n_open:
        return True
    if button_id == 'button-confirm-save-preset' and ts_confirm_save:
         # Check if feedback is a dbc.Alert and its color is "success"
         if (save_feedback_children and 
             isinstance(save_feedback_children, dict) and 
             save_feedback_children.get('props', {}).get('color') == "success"):
             return False # Close modal on successful save
         return True # Keep modal open on error or if feedback is not set yet
    
    if button_id == 'button-cancel-save-preset' and n_cancel:
        return False
            
    return is_open

@dash_app.callback(
    Output('dropdown-load-preset', 'options'),
    [Input('button-analyze', 'n_clicks'), 
     Input('save-preset-feedback', 'children')] 
)
def load_presets_for_dropdown(dummy_input_1, save_feedback_trigger):
    user_id = flask_request.cookies.get('user_token')
    if user_id:
        presets = preset_manager.load_user_presets_list(user_id)
        return presets
    return []

@dash_app.callback(
    [Output('save-preset-feedback', 'children'),
     Output('input-preset-name', 'value', allow_duplicate=True)],
    [Input('button-confirm-save-preset', 'n_clicks')],
    [State('input-preset-name', 'value'),
     State('checklist-conclusions', 'value'), State('checklist-basic-indicators', 'value'),
     State('checklist-advanced-indicators', 'value'), State('checklist-technical-analysis', 'value'),
     State('checklist-volume', 'value'),
     State("input-rsi-period", "value"), State("input-macd-fast-period", "value"), 
     State("input-macd-slow-period", "value"), State("input-macd-signal-period", "value"),
     State("input-bb-period", "value"), State("input-bb-std-dev", "value"),
     State("input-stoch-k-period", "value"), State("input-stoch-d-period", "value"), 
     State("input-stoch-slowing-period", "value"), State("input-atr-period", "value"),
     State("input-ichi-tenkan-period", "value"), State("input-ichi-kijun-period", "value"), 
     State("input-ichi-senkou-b-period", "value"),
     State('input-symbol', 'value'), State('input-interval', 'value'), State('input-num-candles', 'value')
    ],
    prevent_initial_call=True
)
def confirm_save_preset(n_clicks, preset_name,
                        conclusions_val, basic_ind_val, adv_ind_val, tech_an_val, vol_val,
                        rsi_p, macd_f, macd_s, macd_sig, bb_p, bb_std,
                        stoch_k, stoch_d, stoch_slow, atr_p,
                        ichi_t, ichi_k, ichi_sb,
                        symbol_val, interval_val, num_candles_val):
    if not n_clicks:
        raise PreventUpdate

    user_id = flask_request.cookies.get('user_token')
    if not user_id:
        return dbc.Alert("Ошибка: Пользователь не идентифицирован. Войдите снова.", color="warning", dismissable=True), no_update

    if not preset_name:
        return dbc.Alert("Имя пресета не может быть пустым!", color="danger", dismissable=True), no_update
    
    settings = {
        "checklist_conclusions": conclusions_val or [], "checklist_basic_indicators": basic_ind_val or [],
        "checklist_advanced_indicators": adv_ind_val or [], "checklist_technical_analysis": tech_an_val or [],
        "checklist_volume": vol_val or [],
        "params_rsi_period": rsi_p, "params_macd_fast_period": macd_f, 
        "params_macd_slow_period": macd_s, "params_macd_signal_period": macd_sig,
        "params_bb_period": bb_p, "params_bb_std_dev": bb_std,
        "params_stoch_k_period": stoch_k, "params_stoch_d_period": stoch_d, 
        "params_stoch_slowing_period": stoch_slow, "params_atr_period": atr_p,
        "params_ichi_tenkan_period": ichi_t, "params_ichi_kijun_period": ichi_k, 
        "params_ichi_senkou_b_period": ichi_sb,
        "input_symbol": symbol_val, "input_interval": interval_val, "input_num_candles": num_candles_val
    }
    success, message = preset_manager.save_preset(user_id, preset_name, settings)

    if success:
        return dbc.Alert(message, color="success", dismissable=True, duration=4000), "" 
    else:
        return dbc.Alert(message, color="danger", dismissable=True), no_update

@dash_app.callback(
    [Output('checklist-conclusions', 'value'), Output('checklist-basic-indicators', 'value'),
     Output('checklist-advanced-indicators', 'value'), Output('checklist-technical-analysis', 'value'),
     Output('checklist-volume', 'value'),
     Output("input-rsi-period", "value"), Output("input-macd-fast-period", "value"),
     Output("input-macd-slow-period", "value"), Output("input-macd-signal-period", "value"),
     Output("input-bb-period", "value"), Output("input-bb-std-dev", "value"),
     Output("input-stoch-k-period", "value"), Output("input-stoch-d-period", "value"),
     Output("input-stoch-slowing-period", "value"), Output("input-atr-period", "value"),
     Output("input-ichi-tenkan-period", "value"), Output("input-ichi-kijun-period", "value"),
     Output("input-ichi-senkou-b-period", "value"),
     Output('input-symbol', 'value'), Output('input-interval', 'value'), Output('input-num-candles', 'value'),
     Output('save-preset-feedback', 'children', allow_duplicate=True) 
    ],
    [Input('dropdown-load-preset', 'value')],
    prevent_initial_call=True
)
def apply_selected_preset(selected_preset_doc_id):
    if not selected_preset_doc_id:
        raise PreventUpdate

    settings = preset_manager.load_preset_settings(selected_preset_doc_id)
    
    if settings:
        feedback_message = dbc.Alert(f"Пресет '{selected_preset_doc_id}' успешно загружен.", color="info", dismissable=True, duration=3000)
        # Ensure lists for checklists if settings might have None
        concl_val = settings.get("checklist_conclusions") if settings.get("checklist_conclusions") is not None else []
        basic_val = settings.get("checklist_basic_indicators") if settings.get("checklist_basic_indicators") is not None else []
        adv_val = settings.get("checklist_advanced_indicators") if settings.get("checklist_advanced_indicators") is not None else []
        tech_val = settings.get("checklist_technical_analysis") if settings.get("checklist_technical_analysis") is not None else []
        vol_val = settings.get("checklist_volume") if settings.get("checklist_volume") is not None else []
        
        return (
            concl_val, basic_val, adv_val, tech_val, vol_val,
            settings.get("params_rsi_period", 14), settings.get("params_macd_fast_period", 12),
            settings.get("params_macd_slow_period", 26), settings.get("params_macd_signal_period", 9),
            settings.get("params_bb_period", 20), settings.get("params_bb_std_dev", 2.0),
            settings.get("params_stoch_k_period", 14), settings.get("params_stoch_d_period", 3),
            settings.get("params_stoch_slowing_period", 3), settings.get("params_atr_period", 14),
            settings.get("params_ichi_tenkan_period", 9), settings.get("params_ichi_kijun_period", 26),
            settings.get("params_ichi_senkou_b_period", 52),
            settings.get("input_symbol", DEFAULT_SYMBOL), settings.get("input_interval", DEFAULT_INTERVAL),
            settings.get("input_num_candles", DEFAULT_CANDLES),
            feedback_message
        )
    else:
        error_message = dbc.Alert(f"Ошибка загрузки пресета: '{selected_preset_doc_id}'.", color="danger", dismissable=True)
        no_update_list = [no_update] * 20 
        return no_update_list + [error_message]

# Main update_output callback (existing, potentially needs minor adjustments if any state name changed)
@dash_app.callback(
    [
        Output('stored-data','data'),
        Output('stored-analysis','data'),
        Output('main-chart','figure'),
        Output('explanations','children'),
        Output('input-controls-section', 'style'),
        Output('results-section', 'style')
    ],
    [
        Input('button-analyze','n_clicks'),
        Input('button-analyze-loaded','n_clicks'),
        Input('checklist-conclusions','value'),
        Input('checklist-basic-indicators','value'),
        Input('checklist-advanced-indicators','value'),
        Input('checklist-technical-analysis','value'),
        Input('checklist-volume','value'),
        Input("theme-store", "data")
    ],
    [
        State('input-symbol','value'),
        State('input-interval','value'),
        State('input-num-candles','value'),
        State('stored-data','data'),
        State('stored-analysis','data'),
        # Indicator Params States
        State('input-rsi-period', 'value'),
        State('input-macd-fast-period', 'value'),
        State('input-macd-slow-period', 'value'),
        State('input-macd-signal-period', 'value'),
        State('input-bb-period', 'value'),
        State('input-bb-std-dev', 'value'),
        State('input-stoch-k-period', 'value'),
        State('input-stoch-d-period', 'value'),
        State('input-stoch-slowing-period', 'value'),
        State('input-atr-period', 'value'),
        State('input-ichi-tenkan-period', 'value'),
        State('input-ichi-kijun-period', 'value'),
        State('input-ichi-senkou-b-period', 'value'),
    ],
    prevent_initial_call=True
)
async def update_output(n1, n2, concl, basic, adv, tech, vol, theme_store_data,
                        sym, intrvl, ncand, stored_data, stored_analysis,
                        # Indicator params
                        rsi_period_val, macd_fast_val, macd_slow_val, macd_signal_val,
                        bb_period_val, bb_std_dev_val, stoch_k_val, stoch_d_val, stoch_slowing_val,
                        atr_period_val, ichi_tenkan_val, ichi_kijun_val, ichi_senkou_b_val):
    """
    Асинхронный callback FastAPI+Dash, анализирует данные, сохраняет историю,
    формирует график и объяснения. Также управляет видимостью секций UI и темой графика.
    Собирает параметры индикаторов.
    """
    triggered_info = callback_context.triggered[0]
    triggered_prop_id = triggered_info['prop_id']
    triggered = triggered_prop_id.split('.')[0]
    
    user = flask_request.cookies.get('user_token', 'anonymous')
    selected_options = (concl or []) + (basic or []) + (adv or []) + (tech or []) + (vol or []) # Ensure lists

    logger.info(f"Update_output triggered by: {triggered_prop_id}, user: {user}, selected: {selected_options}, sym: {sym}, intrvl: {intrvl}, ncand: {ncand}")

    indicator_params = {
        'rsi_period': rsi_period_val,
        'macd_fast_period': macd_fast_val,
        'macd_slow_period': macd_slow_val,
        'macd_signal_period': macd_signal_val,
        'bb_period': bb_period_val,
        'bb_std_dev': bb_std_dev_val,
        'stoch_k_period': stoch_k_val,
        'stoch_d_period': stoch_d_val,
        'stoch_slowing_period': stoch_slowing_val,
        'atr_period': atr_period_val,
        'ichi_tenkan_period': ichi_tenkan_val,
        'ichi_kijun_period': ichi_kijun_val,
        'ichi_senkou_b_period': ichi_senkou_b_val,
    }
    logger.info(f"Indicator parameters: {indicator_params}")
    
    stored_theme_conf = theme_store_data or {}
    current_theme_mode = stored_theme_conf.get('theme', 'light')
    plotly_template = 'plotly_dark' if current_theme_mode == 'dark' else 'plotly_white'
    logger.info(f"Current theme mode: {current_theme_mode}, plotly template: {plotly_template}")

    input_controls_style = dash.no_update
    results_section_style = dash.no_update

    try:
        if triggered in ['button-analyze', 'button-analyze-loaded']:
            input_controls_style = {'display': 'none'}
            results_section_style = {'display': 'block'}

            if triggered == 'button-analyze' and n1:
                logger.info("Processing 'button-analyze' trigger.")
                result = await analyze_data(user, sym, intrvl, int(ncand), indicator_params=indicator_params) 
                if 'error' in result:
                    return dash.no_update, dash.no_update, dash.no_update, [html.Div(result['error'])], {'display': 'block'}, {'display': 'none'}
                df = await CryptoCompareProvider().fetch_ohlcv(sym, intrvl, int(ncand))
                if df.empty:
                    return dash.no_update, dash.no_update, dash.no_update, [html.Div("Не удалось получить данные для анализа.")], {'display': 'block'}, {'display': 'none'}
                save_history(user, sym, intrvl, result)
                fig = create_chart(selected_options, df, result, plotly_template=plotly_template)
                expl = prepare_explanations(selected_options, result)
                children = [html.H5(e['Название']) for e in expl] + [dcc.Markdown(e['Текст']) for e in expl]
                return df.to_dict('records'), result, fig, children, input_controls_style, results_section_style

            if triggered == 'button-analyze-loaded' and n2:
                logger.info("Processing 'button-analyze-loaded' trigger.")
                history = get_history(user)
                if not history:
                    return dash.no_update, dash.no_update, dash.no_update, [html.Div("История пуста.")], {'display': 'block'}, {'display': 'none'}
                last = history[-1]
                df = await CryptoCompareProvider().fetch_ohlcv(last['symbol'], last['interval'], int(ncand))
                if df.empty:
                    return dash.no_update, dash.no_update, dash.no_update, [html.Div("Не удалось получить данные из истории.")], {'display': 'block'}, {'display': 'none'}
                current_result = last.get('result') 
                fig = create_chart(selected_options, df, current_result, plotly_template=plotly_template) 
                expl = prepare_explanations(selected_options, current_result)
                children = [html.H5(e['Название']) for e in expl] + [dcc.Markdown(e['Текст']) for e in expl]
                return df.to_dict('records'), current_result, fig, children, input_controls_style, results_section_style

        checklist_ids = {
            'checklist-conclusions','checklist-basic-indicators',
            'checklist-advanced-indicators','checklist-technical-analysis',
            'checklist-volume'
        }
        if (triggered in checklist_ids or triggered == 'theme-store') and stored_data and stored_analysis:
            logger.info(f"Processing '{triggered_prop_id}' trigger for checklist/theme update.")
            df = pd.DataFrame(stored_data)
            fig = create_chart(selected_options, df, stored_analysis, plotly_template=plotly_template)
            expl_children = dash.no_update
            if triggered in checklist_ids:
                expl = prepare_explanations(selected_options, stored_analysis)
                expl_children = [html.H5(e['Название']) for e in expl] + [dcc.Markdown(e['Текст']) for e in expl]
            return stored_data, stored_analysis, fig, expl_children, dash.no_update, dash.no_update

    except Exception as e:
        logger.error(f"Exception in update_output: {e}", exc_info=True)
        return dash.no_update, dash.no_update, dash.no_update, [html.Div(f"Произошла внутренняя ошибка: {e}")], {'display': 'block'}, {'display': 'none'}

    raise PreventUpdate


@dash_app.callback(
    [
        Output('input-controls-section', 'style', allow_duplicate=True),
        Output('results-section', 'style', allow_duplicate=True),
        Output('main-chart', 'figure', allow_duplicate=True),
        Output('explanations', 'children', allow_duplicate=True),
        Output('stored-data', 'data', allow_duplicate=True),
        Output('stored-analysis', 'data', allow_duplicate=True),
        Output('input-symbol', 'value'),
        Output('input-interval', 'value'),
        Output('input-num-candles', 'value'),
        Output('checklist-conclusions', 'value'),
        Output('checklist-basic-indicators', 'value'),
        Output('checklist-advanced-indicators', 'value'),
        Output('checklist-technical-analysis', 'value'),
        Output('checklist-volume', 'value'),
        Output('input-rsi-period', 'value'),
        Output('input-macd-fast-period', 'value'),
        Output('input-macd-slow-period', 'value'),
        Output('input-macd-signal-period', 'value'),
        Output('input-bb-period', 'value'),
        Output('input-bb-std-dev', 'value'),
        Output('input-stoch-k-period', 'value'),
        Output('input-stoch-d-period', 'value'),
        Output('input-stoch-slowing-period', 'value'),
        Output('input-atr-period', 'value'),
        Output('input-ichi-tenkan-period', 'value'),
        Output('input-ichi-kijun-period', 'value'),
        Output('input-ichi-senkou-b-period', 'value'),
    ],
    [Input('button-new-analysis', 'n_clicks')],
    prevent_initial_call=True
)
def handle_new_analysis_click(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    
    logger.info(f"'button-new-analysis' clicked {n_clicks} times. Resetting UI and data.")

    default_rsi_period = 14
    default_macd_fast = 12
    default_macd_slow = 26
    default_macd_signal = 9
    default_bb_period = 20
    default_bb_std_dev = 2
    default_stoch_k = 14
    default_stoch_d = 3
    default_stoch_slowing = 3
    default_atr_period = 14
    default_ichi_tenkan = 9
    default_ichi_kijun = 26
    default_ichi_senkou_b = 52

    return (
        {'display': 'block'}, {'display': 'none'}, None, [], None, None,
        DEFAULT_SYMBOL, DEFAULT_INTERVAL, DEFAULT_CANDLES,
        [], [], [], [], [], 
        default_rsi_period, default_macd_fast, default_macd_slow, default_macd_signal,
        default_bb_period, default_bb_std_dev, default_stoch_k, default_stoch_d, default_stoch_slowing,
        default_atr_period, default_ichi_tenkan, default_ichi_kijun, default_ichi_senkou_b
    )
