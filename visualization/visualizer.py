# visualization/visualizer.py

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from visualization.config import VISUAL_CONFIG
from visualization.handlers import HANDLERS

SUBPLOT_INDICATORS = ['MACD','RSI','OBV','ATR','ADX','Stochastic_Oscillator','Volume']

def create_chart(selected_elements, df, analysis_data, plotly_template='plotly_white'):
    indicators = [e for e in selected_elements if e in SUBPLOT_INDICATORS]
    num_rows = 1 + len(indicators)
    row_heights = [0.8] + ([0.2/len(indicators)]*len(indicators) if indicators else [])

    fig = make_subplots(
        rows=num_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=row_heights
    )

    HANDLERS['base'](fig, df, analysis_data=analysis_data)

    for elem in selected_elements:
        if elem in HANDLERS and elem != 'base':
            HANDLERS[elem](fig, df, analysis_data=analysis_data)

    row = 2
    for ind in indicators:
        handler = HANDLERS.get(ind)
        if handler:
            handler(fig, df, analysis_data=analysis_data) # Subplot indicators are drawn on specific rows
        row += 1
    
    current_layout_config = VISUAL_CONFIG['layout'].copy()
    current_layout_config['template'] = plotly_template
    fig.update_layout(**current_layout_config)
    
    return fig

def prepare_explanations(selected_elements, analysis_data):
    from visualization.explanations import prepare_explanations as _prep
    return _prep(selected_elements, analysis_data)
