#!/usr/bin/env python3

# imports
import os
import sys
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# load nat gas data into dataframe
def load_data(filename: str):
    if not os.path.exists(filename):
        print(f"File {filename} does not exist"); sys.exit(1)

    df = None
    with open(filename, "r") as fin:
        try:
            df = pd.read_csv(fin, parse_dates=["Dates"],
                             date_parser=lambda x: pd.to_datetime(x, format="%m/%d/%y"))
        except Exception as e:
            print(f"Failed to read {filename}: {e}")
            sys.exit(1)

    if df is None:
        print(f"Failed to read {filename}"); sys.exit(1)

    df.dropna(inplace=True)

    return df


# Holt-Winters model for optimal price prediction
# this excels with time-series data and seasonal trends
def run_holt_winters(PREDICT_DATE: str, df: pd.DataFrame, debug=False) -> float:

    predict_date = pd.to_datetime(PREDICT_DATE)

    df['Dates'] = pd.to_datetime(df['Dates'], format="%Y-%m-%d")
    df.sort_values('Dates', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # if year and month of predict date are in our training data, return early
    # no need to forecast if this happens
    year_month = pd.Period(year=predict_date.year, month=predict_date.month, freq='M')
    df['YearMonth'] = df['Dates'].dt.to_period('M')  # Extract year and month as period
    if year_month in df['YearMonth'].values:
        predicted_price = float(df.loc[df['YearMonth'] == year_month, 'Prices'].values[0])
        if debug:
            print(f"On {PREDICT_DATE.strftime('%Y-%m-%d')}, the predicted gas price is ${predicted_price:.2f}")
        return predicted_price

    # Calculate the number of months to predict back
    training_day_first = df['Dates'].min()
    training_day_last = df["Dates"].max()
    num_months_back = 0
    if predict_date < training_day_first:
        num_months_back = np.ceil((training_day_first - pd.to_datetime(PREDICT_DATE)).days / 30)
    elif predict_date > training_day_last:
        # if future date > 1 year beyond training data exit with error per reqs
        if (predict_date - training_day_last).days > 366:
            print('Error: Must enter a prediction date within 1 year of training data')
            sys.exit(1)
        num_months_back = 12

    # Fit Holt-Winters model with trend and seasonality for future predictions
    model_hw = ExponentialSmoothing(df['Prices'], trend='add', seasonal='add', seasonal_periods=12)
    fit_hw = model_hw.fit()

    # extrapolate 1 year in future
    future_month_first = (training_day_last + pd.DateOffset(months=1))
    future_dates = pd.date_range(start=future_month_first, periods=12, freq="ME")
    future_forecast = fit_hw.forecast(steps=12)
    forecast_df = pd.DataFrame({"Dates": future_dates, "Forecast": future_forecast.values})

    # Invert the DataFrame for past prediction
    df_inverted = df.iloc[::-1].reset_index(drop=True)

    # Fit the Holt-Winters model on the inverted series for past prediction
    model_hw_inverted = ExponentialSmoothing(df_inverted['Prices'], trend='add', seasonal='add', seasonal_periods=12)
    fit_hw_inverted = model_hw_inverted.fit()

    # Predict backward (on the inverted data)
    sequence_length = abs(int(np.ceil(num_months_back / 12)) * 12)
    past_forecast = fit_hw_inverted.forecast(steps=sequence_length)

    # Create past dates for the inverted forecast
    past_dates = pd.date_range(start=df['Dates'].min() - pd.DateOffset(months=sequence_length),
                                periods=sequence_length, freq="ME")
    past_forecast_df = pd.DataFrame({"Dates": past_dates, "Forecast": past_forecast.values[::-1]})  # Flip back the forecast

    # Function to find the closest date in the forecast
    def find_closest_date(forecast_df, target_date):
        closest_date_idx = np.abs(forecast_df['Dates'] - pd.to_datetime(target_date)).idxmin()
        return forecast_df.iloc[closest_date_idx]

    if predict_date > df['Dates'].max():
        closest_forecast = find_closest_date(forecast_df, PREDICT_DATE)
    else:
        closest_forecast = find_closest_date(past_forecast_df, PREDICT_DATE)

    predicted_price = float(closest_forecast['Forecast'])
    if debug:
        print(f"On {PREDICT_DATE.strftime('%Y-%m-%d')}, the predicted gas price is ${predicted_price:.2f}")

    return predicted_price
