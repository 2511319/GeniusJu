import pandas as pd
import pandas_ta as ta
from config import logger 

def rename_columns_for_ta(df):
    # Проверяет и переименовывает колонки OHLCV к нижнему регистру, если они существуют
    # Это более безопасно, чем просто df.columns = df.columns.str.lower()
    cols_to_rename = {}
    required_cols_lower = ['open', 'high', 'low', 'close'] # 'volume' is optional for some TAs
    
    # Check if all required columns already exist in lowercase
    if all(col in df.columns for col in required_cols_lower):
        # Check for volume separately
        if 'Volume' in df.columns and 'volume' not in df.columns:
            cols_to_rename['Volume'] = 'volume'
        elif 'VOLUME' in df.columns and 'volume' not in df.columns: # Handle all caps case
            cols_to_rename['VOLUME'] = 'volume'
        
        if not cols_to_rename: # No renaming needed for OHLC, and volume is either present or not needed to be renamed
             return df.copy() 
        else: # Only volume needs renaming
            logger.info(f"Переименование колонки volume для pandas-ta: {cols_to_rename}")
            df_renamed = df.rename(columns=cols_to_rename)
            return df_renamed.copy()

    # Proceed if renaming for OHLC is needed
    for col_map_from, col_map_to in {'Open':'open', 'High':'high', 'Low':'low', 'Close':'close', 'Volume':'volume'}.items():
        if col_map_from in df.columns:
            cols_to_rename[col_map_from] = col_map_to
        elif col_map_from.lower() in df.columns and col_map_from.lower() != col_map_to : # e.g. OPEN -> open
             cols_to_rename[col_map_from.lower()] = col_map_to
        # No warning here if a column is simply missing, will be caught later

    # After attempting to map, check if all essential OHLC columns are now present (either originally or after renaming)
    # This check is implicitly done by pandas-ta, but we can be more explicit
    # Create a temporary renamed df to check target columns
    temp_df_for_check = df.rename(columns=cols_to_rename)
    missing_ohlc = [col for col in required_cols_lower if col not in temp_df_for_check.columns]

    if missing_ohlc:
        logger.error(f"Missing critical OHLC columns for TA after attempting rename: {missing_ohlc}. Original columns: {df.columns.tolist()}")
        return df # Return original df, TA will likely fail or be incorrect

    if not cols_to_rename: # This case should be caught by the initial check, but as a safeguard
        logger.info("Нет необходимости в переименовании колонок OHLCV.")
        return df.copy()

    logger.info(f"Переименование колонок для pandas-ta: {cols_to_rename}")
    df_renamed = df.rename(columns=cols_to_rename)
    return df_renamed.copy()


def calculate_all_indicators(df_ohlcv, indicator_params=None):
    if df_ohlcv.empty:
        logger.warning("Получен пустой DataFrame для расчета индикаторов.")
        return df_ohlcv

    df_ta = rename_columns_for_ta(df_ohlcv.copy()) # Use a copy to avoid modifying original df_ohlcv
    
    # Ensure rename_columns_for_ta didn't return the original due to missing columns
    if not all(c in df_ta.columns for c in ['open', 'high', 'low', 'close']):
        logger.error("Не удалось подготовить колонки OHLC для TA. Расчет индикаторов прерван.")
        # Return a copy of the original df_ohlcv, but with no TA columns
        return df_ohlcv.copy() 

    if not isinstance(df_ta.index, pd.DatetimeIndex):
        logger.warning("Индекс DataFrame не является DateTimeIndex. Попытка преобразования 'Open Time'...")
        if 'Open Time' in df_ta.columns:
            try:
                df_ta.index = pd.to_datetime(df_ta['Open Time'])
                logger.info("Индекс успешно преобразован из колонки 'Open Time'.")
            except Exception as e:
                logger.error(f"Ошибка преобразования 'Open Time' в DateTimeIndex: {e}. Расчет индикаторов может быть некорректным.")
                return df_ohlcv.copy()
        elif 'time' in df_ta.columns: # Fallback if 'time' column in lowercase (e.g. from CryptoCompare raw)
             try:
                df_ta.index = pd.to_datetime(df_ta['time'], unit='s')
                logger.info("Индекс успешно преобразован из колонки 'time' (unix s).")
             except Exception as e:
                logger.error(f"Ошибка преобразования 'time' в DateTimeIndex: {e}. Расчет индикаторов может быть некорректным.")
                return df_ohlcv.copy()
        else:
            logger.error("Отсутствует колонка 'Open Time' или 'time' для создания DateTimeIndex. Расчет индикаторов может быть некорректным.")
            return df_ohlcv.copy()


    if indicator_params is None:
        indicator_params = {}
    logger.info(f"Начало расчета индикаторов. Пользовательские параметры: {indicator_params}")

    # 1. RSI
    rsi_period = indicator_params.get('rsi_period', 14)
    df_ta.ta.rsi(length=int(rsi_period), append=True, col_names=(f'RSI_{int(rsi_period)}',))

    # 2. ATR
    atr_period = indicator_params.get('atr_period', 14)
    df_ta.ta.atr(length=int(atr_period), append=True, col_names=(f'ATR_{int(atr_period)}',))
    
    # 3. OBV
    if 'volume' in df_ta.columns:
        df_ta.ta.obv(append=True, col_names=('OBV',))
    else:
        logger.warning("Колонка 'volume' отсутствует, OBV не будет рассчитан.")

    # 4. Stochastic Oscillator
    stoch_k = indicator_params.get('stoch_k_period', 14)
    stoch_d = indicator_params.get('stoch_d_period', 3)
    stoch_slowing = indicator_params.get('stoch_slowing_period', 3)
    df_ta.ta.stoch(k=int(stoch_k), d=int(stoch_d), smooth_k=int(stoch_slowing), append=True, 
                   col_names=(f'STOCHk_{int(stoch_k)}_{int(stoch_d)}_{int(stoch_slowing)}', 
                              f'STOCHd_{int(stoch_k)}_{int(stoch_d)}_{int(stoch_slowing)}'))

    # 5. MACD
    macd_fast = indicator_params.get('macd_fast_period', 12)
    macd_slow = indicator_params.get('macd_slow_period', 26)
    macd_signal = indicator_params.get('macd_signal_period', 9)
    df_ta.ta.macd(fast=int(macd_fast), slow=int(macd_slow), signal=int(macd_signal), append=True, 
                   col_names=(f'MACD_{int(macd_fast)}_{int(macd_slow)}_{int(macd_signal)}', 
                              f'MACDh_{int(macd_fast)}_{int(macd_slow)}_{int(macd_signal)}', 
                              f'MACDs_{int(macd_fast)}_{int(macd_slow)}_{int(macd_signal)}'))

    # 6. Bollinger Bands
    bb_period = indicator_params.get('bb_period', 20)
    bb_std = indicator_params.get('bb_std_dev', 2.0)
    bb_cols = [f'BBL_{int(bb_period)}_{float(bb_std)}', f'BBM_{int(bb_period)}_{float(bb_std)}', 
               f'BBU_{int(bb_period)}_{float(bb_std)}', f'BBB_{int(bb_period)}_{float(bb_std)}',
               f'BBP_{int(bb_period)}_{float(bb_std)}']
    df_ta.ta.bbands(length=int(bb_period), std=float(bb_std), append=True, col_names=tuple(bb_cols))

    # 7. ADX (параметры по умолчанию: length=14)
    adx_cols = (f'ADX_14', f'DMP_14', f'DMN_14')
    df_ta.ta.adx(append=True, col_names=adx_cols)
    
    # 8. Williams %R (параметры по умолчанию: length=14)
    df_ta.ta.willr(append=True, col_names=(f'WILLR_14',))

    # 9. Parabolic SAR (параметры по умолчанию: af0=0.02, af=0.02, max_af=0.2)
    psar_cols = (f'PSARl_0.02_0.2', f'PSARs_0.02_0.2', f'PSARaf_0.02_0.2', f'PSARr_0.02_0.2')
    df_ta.ta.psar(append=True, col_names=psar_cols)

    # 10. Ichimoku Cloud
    ichi_tenkan = indicator_params.get('ichi_tenkan_period', 9)
    ichi_kijun = indicator_params.get('ichi_kijun_period', 26)
    ichi_senkou_b = indicator_params.get('ichi_senkou_b_period', 52)
    # pandas-ta ichimoku returns: SPAN_A, SPAN_B, TENKAN, KIJUN, CHIKOU
    # We will use its default column names or rename them to our custom ones if needed.
    # For now, let's use the default names as they are unique enough.
    # Default names are like: ITS_9, IKS_26, ISA_9_26, ISB_52, ICS_26
    ichimoku_results = df_ta.ta.ichimoku(tenkan=int(ichi_tenkan), kijun=int(ichi_kijun), senkou=int(ichi_senkou_b), append=False)
    if isinstance(ichimoku_results, tuple) and len(ichimoku_results) == 2: # New versions of pandas-ta return a tuple (DataFrame, success_bool)
        ichimoku_df = ichimoku_results[0]
    else: # Older versions might just return the DataFrame
        ichimoku_df = ichimoku_results

    if ichimoku_df is not None and not ichimoku_df.empty:
        # Rename columns to be more descriptive and include parameters
        # Example: ITS_9 -> ICHIMOKU_TENKAN_9, IKS_26 -> ICHIMOKU_KIJUN_26 etc.
        rename_map = {
            f'ITS_{int(ichi_tenkan)}': f'ICHIMOKU_TENKAN_{int(ichi_tenkan)}',
            f'IKS_{int(ichi_kijun)}': f'ICHIMOKU_KIJUN_{int(ichi_kijun)}',
            f'ISA_{int(ichi_tenkan)}_{int(ichi_kijun)}': f'ICHIMOKU_SPAN_A_{int(ichi_tenkan)}_{int(ichi_kijun)}',
            f'ISB_{int(ichi_senkou_b)}': f'ICHIMOKU_SPAN_B_{int(ichi_senkou_b)}',
            f'ICS_{int(ichi_kijun)}': f'ICHIMOKU_CHIKOU_{int(ichi_kijun)}' # Chikou often uses kijun period for its name in pandas-ta
        }
        # Check actual column names in ichimoku_df and rename
        actual_cols = ichimoku_df.columns
        final_rename_map = {}
        for default_name_template, custom_name in rename_map.items():
            # Handle cases where default names might vary slightly based on pandas-ta version or parameters
            # For example, ICS_26 is common if kijun is 26
            if default_name_template in actual_cols:
                 final_rename_map[default_name_template] = custom_name
            # Try to find based on prefix if exact match fails
            elif default_name_template.split('_')[0] in [col.split('_')[0] for col in actual_cols]:
                # This is a bit fragile, assumes only one column starts with 'ITS', 'IKS' etc.
                for actual_col_name in actual_cols:
                    if actual_col_name.startswith(default_name_template.split('_')[0]):
                        final_rename_map[actual_col_name] = custom_name
                        break
        
        if final_rename_map:
            ichimoku_df.rename(columns=final_rename_map, inplace=True)

        df_ta = pd.concat([df_ta, ichimoku_df], axis=1)
    else:
        logger.warning("Расчет Ichimoku не вернул данных.")

    # 11. VWAP (дневной)
    if 'volume' in df_ta.columns:
        df_ta.ta.vwap(anchor="D", append=True, col_names=(f'VWAP_D',))
    else:
        logger.warning("Колонка 'volume' отсутствует, VWAP не будет рассчитан.")

    # 12. Moving Average Envelopes (EMA 20 +/- 2.5%)
    envelope_period = 20
    envelope_percent = 0.025
    ema_col_name = f'EMA_{envelope_period}' # Base EMA column name
    env_mid_col = f'EMA_ENV_MID_{envelope_period}'
    env_upper_col = f'EMA_ENV_UP_{envelope_period}_{envelope_percent*100}%'
    env_lower_col = f'EMA_ENV_LOW_{envelope_period}_{envelope_percent*100}%'
    
    # Calculate EMA first
    df_ta.ta.ema(length=envelope_period, append=True, col_names=(ema_col_name,))
    
    if ema_col_name in df_ta.columns:
        df_ta[env_mid_col] = df_ta[ema_col_name] # The middle band is the EMA itself
        df_ta[env_upper_col] = df_ta[ema_col_name] * (1 + envelope_percent)
        df_ta[env_lower_col] = df_ta[ema_col_name] * (1 - envelope_percent)
        # Optionally drop the base EMA column if only envelopes are needed
        # df_ta.drop(columns=[ema_col_name], inplace=True) 
    else:
        logger.warning(f"Не удалось рассчитать EMA({envelope_period}) для Envelopes.")
            
    logger.info(f"Индикаторы рассчитаны. Колонки в DataFrame: {df_ta.columns.tolist()}")
    return df_ta
