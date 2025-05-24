# dash_app/layout.py

import dash_bootstrap_components as dbc
from dash import dcc, html

TIMEFRAMES = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w']
DEFAULT_SYMBOL = 'BTCUSDT'
DEFAULT_INTERVAL = '4h'
DEFAULT_CANDLES = 144

# Helper function to create icon span for labels
def create_icon_label(text, value, icon_class="bi-graph-up"):
    return html.Span([html.I(className=f"bi {icon_class} me-2"), text], id=f"tip_{value}")

# Tooltip descriptions
tooltip_data = {
    'primary_analysis': ("Общий первичный анализ текущей рыночной ситуации.", "bi-card-text"),
    'confidence_in_trading_decisions': ("Оценка уверенности в принятии торговых решений на основе текущих данных.", "bi-check-circle"),
    'indicator_correlations': ("Анализ корреляции между различными техническими индикаторами.", "bi-diagram-3"),
    'volatility_by_intervals': ("Оценка волатильности на различных временных интервалах.", "bi-activity"),
    'market_cycles_identification': ("Идентификация текущей фазы рыночного цикла.", "bi-arrow-repeat"),
    'extended_ichimoku_analysis': ("Расширенный анализ с использованием индикатора Ишимоку.", "bi-cloud-sun"), # Example icon
    'RSI': ("Relative Strength Index (Индекс Относительной Силы) - осциллятор, измеряющий скорость и изменение ценовых движений для определения перекупленности/перепроданности.", "bi-calculator-fill"),
    'MACD': ("Moving Average Convergence Divergence - трендовый осциллятор, показывающий соотношение между двумя скользящими средними цены.", "bi-graph-up-arrow"),
    'OBV': ("On-Balance Volume (Балансовый Объем) - индикатор, связывающий объем торгов с изменением цены.", "bi-bar-chart-line-fill"),
    'ATR': ("Average True Range (Средний Истинный Диапазон) - индикатор волатильности рынка.", "bi-arrows-fullscreen"),
    'Stochastic_Oscillator': ("Stochastic Oscillator (Стохастический Осциллятор) - индикатор, показывающий положение текущей цены относительно диапазона цен за определенный период.", "bi-sliders"),
    'ADX': ("Average Directional Index (Индекс Среднего Направления Движения) - индикатор силы тренда.", "bi-signpost-split-fill"),
    'Bollinger_Bands': ("Bollinger Bands (Линии Боллинджера) - индикатор волатильности, состоящий из скользящей средней и двух стандартных отклонений.", "bi-distribute-vertical"),
    'Ichimoku_Cloud': ("Ichimoku Cloud (Облако Ишимоку) - комплексный индикатор, предоставляющий информацию о направлении тренда, уровнях поддержки/сопротивления и силе сигналов.", "bi-cloud-fill"),
    'Parabolic_SAR': ("Parabolic Stop and Reverse (Параболическая Система Остановки и Разворота) - индикатор для определения точек разворота тренда.", "bi-record-circle-fill"),
    'VWAP': ("Volume Weighted Average Price (Средневзвешенная по Объему Цена) - индикатор, показывающий среднюю цену актива с учетом объема торгов.", "bi-hash"),
    'Moving_Average_Envelopes': ("Moving Average Envelopes (Конверты Скользящих Средних) - линии, построенные выше и ниже скользящей средней на определенном расстоянии.", "bi-bounding-box-circles"),
    'support_resistance_levels': ("Определение ключевых уровней поддержки и сопротивления.", "bi-rulers"),
    'trend_lines': ("Построение и анализ линий тренда.", "bi-graph-down"),
    'fibonacci_analysis': ("Анализ с использованием уровней Фибоначчи.", "bi-pentagon"),
    'candlestick_patterns': ("Распознавание и интерпретация свечных моделей.", "bi-bar-chart-steps"),
    'volume': ("Анализ объемов торгов.", "bi-reception-4"),
    # Placeholders for others
    'elliott_wave_analysis': ("Описание для Elliott Waves будет добавлено позже.", "bi-water"),
    'imbalances': ("Описание для Imbalances будет добавлено позже.", "bi-lightning-charge"),
    'unfinished_zones': ("Описание для Unfinished Zones будет добавлено позже.", "bi-patch-question"),
    'divergence_analysis': ("Описание для Divergence Analysis будет добавлено позже.", "bi-arrows-angle-expand"),
    'structural_edge': ("Описание для Structural Edge будет добавлено позже.", "bi-border-style"),
    'gap_analysis': ("Описание для Gaps будет добавлено позже.", "bi-code-square"),
    'fair_value_gaps': ("Описание для Fair Value Gaps будет добавлено позже.", "bi-bounding-box"),
    'psychological_levels': ("Описание для Psychological Levels будет добавлено позже.", "bi-heart-pulse"),
    'anomalous_candles': ("Описание для Anomalous Candles будет добавлено позже.", "bi-exclamation-diamond"),
    'price_prediction': ("Описание для Price Prediction будет добавлено позже.", "bi-magic"),
    'recommendations': ("Описание для Recommendations будет добавлено позже.", "bi-hand-thumbs-up"),
}

# Generate options and tooltips
checklist_options = {
    'conclusions': [
        {'label': create_icon_label('Primary Analysis', 'primary_analysis', tooltip_data['primary_analysis'][1]), 'value': 'primary_analysis'},
        {'label': create_icon_label('Confidence In Trading Decisions', 'confidence_in_trading_decisions', tooltip_data['confidence_in_trading_decisions'][1]), 'value': 'confidence_in_trading_decisions'},
        {'label': create_icon_label('Indicator Correlations', 'indicator_correlations', tooltip_data['indicator_correlations'][1]), 'value': 'indicator_correlations'},
        {'label': create_icon_label('Volatility By Intervals', 'volatility_by_intervals', tooltip_data['volatility_by_intervals'][1]), 'value': 'volatility_by_intervals'},
        {'label': create_icon_label('Market Cycles Identification', 'market_cycles_identification', tooltip_data['market_cycles_identification'][1]), 'value': 'market_cycles_identification'},
        {'label': create_icon_label('Extended Ichimoku Analysis', 'extended_ichimoku_analysis', tooltip_data['extended_ichimoku_analysis'][1]), 'value': 'extended_ichimoku_analysis'},
    ],
    'basic_indicators': [
        {'label': create_icon_label('RSI', 'RSI', tooltip_data['RSI'][1]), 'value': 'RSI'},
        {'label': create_icon_label('MACD', 'MACD', tooltip_data['MACD'][1]), 'value': 'MACD'},
        {'label': create_icon_label('OBV', 'OBV', tooltip_data['OBV'][1]), 'value': 'OBV'},
        {'label': create_icon_label('ATR', 'ATR', tooltip_data['ATR'][1]), 'value': 'ATR'},
        {'label': create_icon_label('Stochastic Oscillator', 'Stochastic_Oscillator', tooltip_data['Stochastic_Oscillator'][1]), 'value': 'Stochastic_Oscillator'},
        {'label': create_icon_label('ADX', 'ADX', tooltip_data['ADX'][1]), 'value': 'ADX'},
    ],
    'advanced_indicators': [
        {'label': create_icon_label('Bollinger Bands', 'Bollinger_Bands', tooltip_data['Bollinger_Bands'][1]), 'value': 'Bollinger_Bands'},
        {'label': create_icon_label('Ichimoku Cloud', 'Ichimoku_Cloud', tooltip_data['Ichimoku_Cloud'][1]), 'value': 'Ichimoku_Cloud'},
        {'label': create_icon_label('Parabolic SAR', 'Parabolic_SAR', tooltip_data['Parabolic_SAR'][1]), 'value': 'Parabolic_SAR'},
        {'label': create_icon_label('VWAP', 'VWAP', tooltip_data['VWAP'][1]), 'value': 'VWAP'},
        {'label': create_icon_label('Moving Average Envelopes', 'Moving_Average_Envelopes', tooltip_data['Moving_Average_Envelopes'][1]), 'value': 'Moving_Average_Envelopes'},
    ],
    'technical_analysis': [
        {'label': create_icon_label('Support/Resistance', 'support_resistance_levels', tooltip_data['support_resistance_levels'][1]), 'value': 'support_resistance_levels'},
        {'label': create_icon_label('Trend Lines', 'trend_lines', tooltip_data['trend_lines'][1]), 'value': 'trend_lines'},
        {'label': create_icon_label('Fibonacci Levels', 'fibonacci_analysis', tooltip_data['fibonacci_analysis'][1]), 'value': 'fibonacci_analysis'},
        {'label': create_icon_label('Elliott Waves', 'elliott_wave_analysis', tooltip_data['elliott_wave_analysis'][1]), 'value': 'elliott_wave_analysis'},
        {'label': create_icon_label('Imbalances', 'imbalances', tooltip_data['imbalances'][1]), 'value': 'imbalances'},
        {'label': create_icon_label('Unfinished Zones', 'unfinished_zones', tooltip_data['unfinished_zones'][1]), 'value': 'unfinished_zones'},
        {'label': create_icon_label('Divergence Analysis', 'divergence_analysis', tooltip_data['divergence_analysis'][1]), 'value': 'divergence_analysis'},
        {'label': create_icon_label('Structural Edge', 'structural_edge', tooltip_data['structural_edge'][1]), 'value': 'structural_edge'},
        {'label': create_icon_label('Candlestick Patterns', 'candlestick_patterns', tooltip_data['candlestick_patterns'][1]), 'value': 'candlestick_patterns'},
        {'label': create_icon_label('Gaps', 'gap_analysis', tooltip_data['gap_analysis'][1]), 'value': 'gap_analysis'},
        {'label': create_icon_label('Fair Value Gaps', 'fair_value_gaps', tooltip_data['fair_value_gaps'][1]), 'value': 'fair_value_gaps'},
        {'label': create_icon_label('Psychological Levels', 'psychological_levels', tooltip_data['psychological_levels'][1]), 'value': 'psychological_levels'},
        {'label': create_icon_label('Anomalous Candles', 'anomalous_candles', tooltip_data['anomalous_candles'][1]), 'value': 'anomalous_candles'},
        {'label': create_icon_label('Price Prediction', 'price_prediction', tooltip_data['price_prediction'][1]), 'value': 'price_prediction'},
        {'label': create_icon_label('Recommendations', 'recommendations', tooltip_data['recommendations'][1]), 'value': 'recommendations'},
    ],
    'volume': [
        {'label': create_icon_label('Volume', 'volume', tooltip_data['volume'][1]), 'value': 'volume'}
    ]
}

tooltips_components = [
    dbc.Tooltip(tooltip_data[value][0], target=f"tip_{value}", placement="top")
    for value in tooltip_data
]


layout = dbc.Container([
    html.Link(id='theme-link', rel='stylesheet', href=dbc.themes.FLATLY),
    dcc.Store(id='theme-store', storage_type='local'),

    html.Div([ # Обертка для группы элементов управления пресетами
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='dropdown-load-preset', placeholder="Загрузить пресет...", className="mb-2"), width=12, sm=12, md=6), # md=6 чтобы на средних экранах занимало половину
            dbc.Col(dbc.Button("Сохранить текущий пресет", id='button-open-save-modal', n_clicks=0, className="mb-2 w-100"), width=12, sm=12, md=6)
        ], className="mb-3 g-2"), # g-2 для небольшого промежутка между колонками, если они в одну строку

        dbc.Modal(id='modal-save-preset', is_open=False, centered=True, children=[
            dbc.ModalHeader(dbc.ModalTitle("Сохранить текущие настройки как пресет")),
            dbc.ModalBody([
                dbc.Label("Имя пресета:", html_for="input-preset-name"),
                dbc.Input(id='input-preset-name', placeholder="Например, 'RSI + MACD для BTC'", className="mb-3"),
                html.Div(id="save-preset-feedback") # Для сообщений типа "Пресет сохранен!" или ошибок
            ]),
            dbc.ModalFooter([
                dbc.Button("Отмена", id="button-cancel-save-preset", color="secondary", className="ms-auto"), # ms-auto для выравнивания вправо
                dbc.Button("Сохранить", id='button-confirm-save-preset', color="primary")
            ])
        ]),
    ], style={'padding': '10px', 'borderBottom': '1px solid #eee', 'marginBottom': '15px'}),

    dcc.Store(id='stored-data'),
    dcc.Store(id='stored-analysis'),

    dbc.Row([
        dbc.Col(html.H3('ChartGenius2'), width='auto'),
        dbc.Col(dbc.Switch(id="theme-switch", label="Темная тема", value=False), width='auto', className="ms-auto align-self-center")
    ], align="center", className="mb-4"),

    html.Div(id='input-controls-section', children=[
        dbc.Row([
            dbc.Col([
                dbc.Input(id='input-symbol', placeholder='Символ', type='text', value=DEFAULT_SYMBOL, className='mb-2'),
                dcc.Dropdown(
                    id='input-interval',
                    options=[{'label': tf, 'value': tf} for tf in TIMEFRAMES],
                    value=DEFAULT_INTERVAL,  # Default value
                    clearable=False,
                    className='mb-2',
                    placeholder='Выберите интервал'
                ),
                dbc.Input(id='input-num-candles', placeholder='Кол-во свечей', type='number', value=DEFAULT_CANDLES, className='mb-2'),
                dbc.Button('Собрать и Анализировать', id='button-analyze', color='primary', className='me-2 mb-2'),
                dbc.Button('Анализировать из истории', id='button-analyze-loaded', color='secondary')
            ], xs=12, sm=12, md=4, lg=3),

            dbc.Col([
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            dbc.Checklist(
                                options=checklist_options['conclusions'],
                                value=[], id='checklist-conclusions', switch=True
                            ),
                            title="Выводы"
                        ),
                        dbc.AccordionItem(
                            [
                                dbc.Checklist(
                                    options=checklist_options['basic_indicators'],
                                    value=[], id='checklist-basic-indicators', switch=True
                                ),
                                html.Div(id="settings-RSI-params", style={'display': 'none', 'padding-top': '10px', 'border-top': '1px solid #eee', 'margin-top': '10px'}, children=[
                                    html.H6("Настройки RSI:", className="mt-2"),
                                    dbc.Label("Период:", html_for="input-rsi-period", className="fw-bold"),
                                    dbc.Input(id="input-rsi-period", type="number", value=14, min=2, max=100, step=1, size="sm", className="mb-2")
                                ]),
                                html.Div(id="settings-MACD-params", style={'display': 'none', 'padding-top': '10px', 'border-top': '1px solid #eee', 'margin-top': '10px'}, children=[
                                    html.H6("Настройки MACD:", className="mt-2"),
                                    dbc.Label("Быстрый период:", html_for="input-macd-fast-period", className="fw-bold"),
                                    dbc.Input(id="input-macd-fast-period", type="number", value=12, min=2, max=100, step=1, size="sm", className="mb-2"),
                                    dbc.Label("Медленный период:", html_for="input-macd-slow-period", className="fw-bold"),
                                    dbc.Input(id="input-macd-slow-period", type="number", value=26, min=2, max=200, step=1, size="sm", className="mb-2"),
                                    dbc.Label("Сигнальный период:", html_for="input-macd-signal-period", className="fw-bold"),
                                    dbc.Input(id="input-macd-signal-period", type="number", value=9, min=1, max=50, step=1, size="sm", className="mb-2"),
                                ]),
                                html.Div(id="settings-Stochastic_Oscillator-params", style={'display': 'none', 'padding-top': '10px', 'border-top': '1px solid #eee', 'margin-top': '10px'}, children=[
                                    html.H6("Настройки Stochastic Oscillator:", className="mt-2"),
                                    dbc.Label("K Период:", html_for="input-stoch-k-period", className="fw-bold"),
                                    dbc.Input(id="input-stoch-k-period", type="number", value=14, min=1, max=100, step=1, size="sm", className="mb-2"),
                                    dbc.Label("D Период:", html_for="input-stoch-d-period", className="fw-bold"),
                                    dbc.Input(id="input-stoch-d-period", type="number", value=3, min=1, max=50, step=1, size="sm", className="mb-2"),
                                    dbc.Label("Замедление (Slowing):", html_for="input-stoch-slowing-period", className="fw-bold"),
                                    dbc.Input(id="input-stoch-slowing-period", type="number", value=3, min=1, max=50, step=1, size="sm", className="mb-2"),
                                ]),
                                html.Div(id="settings-ATR-params", style={'display': 'none', 'padding-top': '10px', 'border-top': '1px solid #eee', 'margin-top': '10px'}, children=[
                                    html.H6("Настройки ATR:", className="mt-2"),
                                    dbc.Label("Период:", html_for="input-atr-period", className="fw-bold"),
                                    dbc.Input(id="input-atr-period", type="number", value=14, min=1, max=100, step=1, size="sm", className="mb-2"),
                                ]),
                            ],
                            title="Базовые индикаторы"
                        ),
                        dbc.AccordionItem(
                            [
                                dbc.Checklist(
                                    options=checklist_options['advanced_indicators'],
                                    value=[], id='checklist-advanced-indicators', switch=True
                                ),
                                html.Div(id="settings-Bollinger_Bands-params", style={'display': 'none', 'padding-top': '10px', 'border-top': '1px solid #eee', 'margin-top': '10px'}, children=[
                                    html.H6("Настройки Bollinger Bands:", className="mt-2"),
                                    dbc.Label("Период:", html_for="input-bb-period", className="fw-bold"),
                                    dbc.Input(id="input-bb-period", type="number", value=20, min=2, max=100, step=1, size="sm", className="mb-2"),
                                    dbc.Label("Стандартное отклонение:", html_for="input-bb-std-dev", className="fw-bold"),
                                    dbc.Input(id="input-bb-std-dev", type="number", value=2, min=0.1, max=5, step=0.1, size="sm", className="mb-2"),
                                ]),
                                html.Div(id="settings-Ichimoku_Cloud-params", style={'display': 'none', 'padding-top': '10px', 'border-top': '1px solid #eee', 'margin-top': '10px'}, children=[
                                    html.H6("Настройки Ichimoku Cloud:", className="mt-2"),
                                    dbc.Label("Tenkan-sen период:", html_for="input-ichi-tenkan-period", className="fw-bold"),
                                    dbc.Input(id="input-ichi-tenkan-period", type="number", value=9, min=1, max=50, step=1, size="sm", className="mb-2"),
                                    dbc.Label("Kijun-sen период:", html_for="input-ichi-kijun-period", className="fw-bold"),
                                    dbc.Input(id="input-ichi-kijun-period", type="number", value=26, min=1, max=100, step=1, size="sm", className="mb-2"),
                                    dbc.Label("Senkou Span B период:", html_for="input-ichi-senkou-b-period", className="fw-bold"),
                                    dbc.Input(id="input-ichi-senkou-b-period", type="number", value=52, min=1, max=200, step=1, size="sm", className="mb-2"),
                                ]),
                            ],
                            title="Продвинутые индикаторы"
                        ),
                        dbc.AccordionItem(
                            dbc.Checklist(
                                options=checklist_options['technical_analysis'],
                                value=[], id='checklist-technical-analysis',
                                switch=True, style={'maxHeight':'200px','overflowY':'auto'}
                            ),
                            title="Технический анализ"
                        ),
                        dbc.AccordionItem(
                            dbc.Checklist(
                                options=checklist_options['volume'],
                                value=[], id='checklist-volume', switch=True
                            ),
                            title="Объём"
                        ),
                    ],
                    start_collapsed=True,
                    always_open=True # Allows multiple items to be open
                )
            ], xs=12, sm=12, md=8, lg=9),
        ], className='mb-4'),
    ]), # End of input-controls-section

    dcc.Loading(id="loading-results", type="default", children=[
        html.Div([ # Обертка для прогресс-бара и сообщения
            dbc.Progress(id="loading-progress-bar", value=0, striped=True, animated=True, style={"height": "20px"}, className="mb-1"),
            html.Div(id="loading-progress-message", children="Анализ запускается...", className="text-center small text-muted")
        ], style={'min-height': '60px', 'padding-top':'10px'}),
        html.Div(id='results-section', style={'display': 'none'}, children=[
            dbc.Button('Новый анализ', id='button-new-analysis', color='info', className='mb-2'),
            dbc.Row(dbc.Col(dcc.Graph(id='main-chart', config={'responsive': True}), width=12)),
            dbc.Row(dbc.Col(html.Div(id='explanations'), width=12)),
        ])
    ]), # End of Loading and results-section
    html.Div(tooltips_components) # Add tooltips here
], fluid=True)
