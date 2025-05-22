# visualization/config.py

VISUAL_CONFIG = {
    'layout': {
        'xaxis_rangeslider_visible': False,
        'template': 'plotly_dark',
        'height': 600,
        'dragmode': 'pan',
    },
    'colors': {
        'bollinger_upper': 'rgba(173,216,230,0.5)',
        'bollinger_lower': 'rgba(173,216,230,0.2)',
        'bollinger_middle': 'blue',
        'ichimoku_a': 'rgba(255,0,0,0.5)',
        'ichimoku_b': 'rgba(0,255,0,0.5)',
        'parabolic_sar': 'blue',
        'vwap': 'orange',
        'ma_env': 'green',
        'support': 'green',
        'resistance': 'red',
        'fib_global': 'purple',
        'fib_local': 'green',
    },
    'line_styles': {
        'support': {'dash': 'dash'},
        'resistance': {'dash': 'dash'},
        'fib': {'dash': 'dash'},
    }
}
