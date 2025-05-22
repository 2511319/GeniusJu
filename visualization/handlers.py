# visualization/handlers.py

import plotly.graph_objects as go
from visualization.config import VISUAL_CONFIG

def base_candlestick(fig, df, **kwargs):
    fig.add_trace(go.Candlestick(
        x=df['Open Time'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='OHLC'
    ), row=1, col=1)

def add_bollinger(fig, df, **kwargs):
    c = VISUAL_CONFIG['colors']
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Bollinger_Upper'],
        line=dict(color=c['bollinger_upper']), name='BB Upper',
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Bollinger_Lower'],
        line=dict(color=c['bollinger_lower']), fill='tonexty',
        fillcolor=c['bollinger_lower'], name='BB Lower',
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Bollinger_Middle'],
        line=dict(color=c['bollinger_middle']), name='BB Middle',
        showlegend=False
    ), row=1, col=1)

def add_ichimoku(fig, df, **kwargs):
    c = VISUAL_CONFIG['colors']
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Ichimoku_A'],
        line=dict(color=c['ichimoku_a']), name='Ichimoku A',
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Ichimoku_B'],
        line=dict(color=c['ichimoku_b']), fill='tonexty',
        fillcolor=c['ichimoku_b'], name='Ichimoku B',
        showlegend=False
    ), row=1, col=1)

def add_parabolic_sar(fig, df, **kwargs):
    c = VISUAL_CONFIG['colors']
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Parabolic_SAR'],
        mode='markers',
        marker=dict(color=c['parabolic_sar'], size=4, symbol='circle'),
        name='Parabolic SAR',
        showlegend=False
    ), row=1, col=1)

def add_vwap(fig, df, **kwargs):
    c = VISUAL_CONFIG['colors']
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['VWAP'],
        line=dict(color=c['vwap']), name='VWAP',
        showlegend=False
    ), row=1, col=1)

def add_ma_envelopes(fig, df, **kwargs):
    c = VISUAL_CONFIG['colors']
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Moving_Average_Envelope_Upper'],
        line=dict(color=c['ma_env']), name='MA Envelope Upper',
        showlegend=False
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=df['Open Time'], y=df['Moving_Average_Envelope_Lower'],
        line=dict(color=c['ma_env']), fill='tonexty',
        fillcolor=c['ma_env'], name='MA Envelope Lower',
        showlegend=False
    ), row=1, col=1)

def add_support_resistance(fig, df, analysis_data, **kwargs):
    c = VISUAL_CONFIG['colors']
    levels = analysis_data.get('support_resistance_levels', {})
    for sup in levels.get('supports', []):
        fig.add_trace(go.Scatter(
            x=[sup['date'], df['Open Time'].iloc[-1]],
            y=[sup['level'], sup['level']],
            mode='lines', line=dict(color=c['support'], **VISUAL_CONFIG['line_styles']['support']),
            showlegend=False
        ), row=1, col=1)
    for res in levels.get('resistances', []):
        fig.add_trace(go.Scatter(
            x=[res['date'], df['Open Time'].iloc[-1]],
            y=[res['level'], res['level']],
            mode='lines', line=dict(color=c['resistance'], **VISUAL_CONFIG['line_styles']['resistance']),
            showlegend=False
        ), row=1, col=1)

def add_fibonacci(fig, df, analysis_data, trend_type='based_on_global_trend', **kwargs):
    c = VISUAL_CONFIG['colors']
    fib = analysis_data.get('fibonacci_analysis', {}).get(trend_type, {})
    levels = fib.get('levels', {})
    style = VISUAL_CONFIG['line_styles']['fib']
    color = c['fib_global'] if trend_type=='based_on_global_trend' else c['fib_local']
    for name, price in levels.items():
        fig.add_trace(go.Scatter(
            x=[fib['start_point']['date'], fib['end_point']['date']],
            y=[price, price],
            mode='lines',
            line=dict(color=color, **style),
            showlegend=False
        ), row=1, col=1)

HANDLERS = {
    'base': base_candlestick,
    'Bollinger_Bands': add_bollinger,
    'Ichimoku_Cloud': add_ichimoku,
    'Parabolic_SAR': add_parabolic_sar,
    'VWAP': add_vwap,
    'Moving_Average_Envelopes': add_ma_envelopes,
    'support_resistance_levels': add_support_resistance,
    'fibonacci_global': lambda fig, df, ad, **kw: add_fibonacci(fig, df, ad, 'based_on_global_trend'),
    'fibonacci_local':  lambda fig, df, ad, **kw: add_fibonacci(fig, df, ad, 'based_on_local_trend'),
}
