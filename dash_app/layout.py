# dash_app/layout.py

import dash_bootstrap_components as dbc
from dash import dcc, html

layout = dbc.Container([
    dcc.Store(id='stored-data'),
    dcc.Store(id='stored-analysis'),

    dbc.Row(dbc.Col(html.H3('ChartGenius2'), width=12)),

    dbc.Row([
        dbc.Col([
            dbc.Input(id='input-symbol', placeholder='Символ', type='text', value='BTCUSDT', className='mb-2'),
            dbc.Input(id='input-interval', placeholder='Интервал', type='text', value='4h', className='mb-2'),
            dbc.Input(id='input-num-candles', placeholder='Кол-во свечей', type='number', value=144, className='mb-2'),
            dbc.Button('Собрать и Анализировать', id='button-analyze', color='primary', className='me-2 mb-2'),
            dbc.Button('Анализировать из истории', id='button-analyze-loaded', color='secondary')
        ], width=3),

        dbc.Col([
            html.H5('Выводы'),
            dbc.Checklist(
                options=[
                    {'label':'Primary Analysis','value':'primary_analysis'},
                    {'label':'Confidence In Trading Decisions','value':'confidence_in_trading_decisions'},
                    {'label':'Indicator Correlations','value':'indicator_correlations'},
                    {'label':'Volatility By Intervals','value':'volatility_by_intervals'},
                    {'label':'Market Cycles Identification','value':'market_cycles_identification'},
                    {'label':'Extended Ichimoku Analysis','value':'extended_ichimoku_analysis'},
                ],
                value=[], id='checklist-conclusions', switch=True
            ),
            html.H5('Базовые индикаторы'),
            dbc.Checklist(
                options=[
                    {'label':'RSI','value':'RSI'},
                    {'label':'MACD','value':'MACD'},
                    {'label':'OBV','value':'OBV'},
                    {'label':'ATR','value':'ATR'},
                    {'label':'Stochastic Oscillator','value':'Stochastic_Oscillator'},
                    {'label':'ADX','value':'ADX'},
                ],
                value=[], id='checklist-basic-indicators', switch=True
            ),
            html.H5('Продвинутые индикаторы'),
            dbc.Checklist(
                options=[
                    {'label':'Bollinger Bands','value':'Bollinger_Bands'},
                    {'label':'Ichimoku Cloud','value':'Ichimoku_Cloud'},
                    {'label':'Parabolic SAR','value':'Parabolic_SAR'},
                    {'label':'VWAP','value':'VWAP'},
                    {'label':'Moving Average Envelopes','value':'Moving_Average_Envelopes'},
                ],
                value=[], id='checklist-advanced-indicators', switch=True
            ),
            html.H5('Технический анализ'),
            dbc.Checklist(
                options=[
                    {'label':'Support/Resistance','value':'support_resistance_levels'},
                    {'label':'Trend Lines','value':'trend_lines'},
                    {'label':'Fibonacci Levels','value':'fibonacci_analysis'},
                    {'label':'Elliott Waves','value':'elliott_wave_analysis'},
                    {'label':'Imbalances','value':'imbalances'},
                    {'label':'Unfinished Zones','value':'unfinished_zones'},
                    {'label':'Divergence Analysis','value':'divergence_analysis'},
                    {'label':'Structural Edge','value':'structural_edge'},
                    {'label':'Candlestick Patterns','value':'candlestick_patterns'},
                    {'label':'Gaps','value':'gap_analysis'},
                    {'label':'Fair Value Gaps','value':'fair_value_gaps'},
                    {'label':'Psychological Levels','value':'psychological_levels'},
                    {'label':'Anomalous Candles','value':'anomalous_candles'},
                    {'label':'Price Prediction','value':'price_prediction'},
                    {'label':'Recommendations','value':'recommendations'},
                ],
                value=[], id='checklist-technical-analysis',
                switch=True, style={'maxHeight':'200px','overflowY':'auto'}
            ),
            html.H5('Объём'),
            dbc.Checklist(
                options=[{'label':'Volume','value':'volume'}],
                value=[], id='checklist-volume', switch=True
            ),
        ], width=9),
    ], className='mb-4'),

    dbc.Row(dbc.Col(dcc.Graph(id='main-chart'), width=12)),
    dbc.Row(dbc.Col(html.Div(id='explanations'), width=12)),
], fluid=True)
