"""
Main application module for Time Series Analysis using Flask.

This module initializes a Flask application that provides endpoints to fetch data
from a Google Spreadsheet, perform time series analysis using ARIMA and ARIMAX models,
and return the Mean Absolute Percentage Error (MAPE) for each model.

The application relies on Google Cloud Platform credentials to access the spreadsheet.
"""

import pandas as pd
# from google.colab import auth
import google.auth
import gspread
import os
import json
import base64
from flask import Flask

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error

from google.oauth2.service_account import Credentials

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = json.loads(base64.b64decode(os.environ.get("GCP_CREDS")).decode("utf-8"))

def create_data_frame():
    """
    Fetches data from a Google Spreadsheet and creates pandas DataFrames.

    This function authenticates with Google Sheets using service account credentials,
    opens a specific spreadsheet (ID hardcoded), and iterates through its worksheets.
    It creates a pandas DataFrame for each relevant worksheet (excluding "Data" and
    "CorrelationResults"). The DataFrames are stored in the global scope using the
    worksheet title as the variable name. It also attempts to convert numeric columns
    to float.

    Returns:
        list: A list of strings containing the names of the sheets that were processed.
    """
    gc = gspread.service_account_from_dict(credentials, scopes=scopes)

    spreadsheet_key = '1jnTFKyRtwLc1cK1YXQ3GER_z8dYmpsj0VmB9nih-szQ'
    spreadsheet = gc.open_by_key(spreadsheet_key)

    all_sheet_names = [worksheet.title for worksheet in spreadsheet.worksheets()]

    relevant_sheet_names = [sheet_name for sheet_name in all_sheet_names if sheet_name not in ["Data", "CorrelationResults"]]


    for sheet_name in relevant_sheet_names:
      try:
        worksheet = spreadsheet.worksheet(sheet_name)
        rows = worksheet.get_all_values()

        df = pd.DataFrame.from_records(rows[1:], columns=rows[0])

        for col in df.columns:
            if col != 'Date':
                try:
                    df[col] = df[col].astype(float)
                except ValueError:
                    print(f"Could not convert column '{col}' to float in sheet '{sheet_name}'. Skipping conversion for this column.")
                    pass

        globals()[sheet_name] = df
        print(f"DataFrame '{sheet_name}' created successfully.")

      except Exception as e:
        print(f"An error occurred while processing sheet '{sheet_name}': {e}")
    return relevant_sheet_names

# relevant_sheet_names = create_data_frame()


def generate_results(relevant_sheet_names):
    """
    Generates time series analysis results for the given sheets.

    This function iterates through the list of sheet names, retrieves the corresponding
    DataFrames from the global scope, and performs ARIMA and ARIMAX modeling.
    It splits the data into training (all but last 30 rows) and testing (last 30 rows) sets.
    It calculates the Mean Absolute Percentage Error (MAPE) for both models.

    Args:
        relevant_sheet_names (list): A list of strings representing the names of the sheets to analyze.

    Returns:
        dict: A dictionary where keys are sheet names and values are dictionaries containing
              'ARIMA' and/or 'ARIMAX' MAPE scores.
              Example: {'Sheet1': {'ARIMA': 0.05, 'ARIMAX': 0.04}}
    """
    results = {}
    for sheet_name in relevant_sheet_names:
        try:
            df = globals()[sheet_name]
            if len(df) < 30:
                print(f"Skipping sheet '{sheet_name}' due to insufficient data.")
                continue

            train = df[:-30]
            test = df[-30:]

            try:
                model_arima = ARIMA(train.iloc[:, 1], order=(5, 1, 0))
                model_arima_fit = model_arima.fit()
                predictions_arima = model_arima_fit.predict(start=len(train), end=len(df)-1)
                mape_arima = mean_absolute_percentage_error(test.iloc[:, 1], predictions_arima)
                print(f"Sheet '{sheet_name}': ARIMA MAPE = {mape_arima}")
                if sheet_name not in results:
                    results[sheet_name] = {}
                results[sheet_name]['ARIMA'] = mape_arima
            except Exception as e:
                print(f"Error fitting ARIMA model for sheet '{sheet_name}': {e}")

            try:
                exog_cols = list(range(2, len(df.columns)))
                model_arimax = SARIMAX(train.iloc[:, 1], exog=train.iloc[:, exog_cols], order=(5, 1, 0))
                model_arimax_fit = model_arimax.fit()
                predictions_arimax = model_arimax_fit.predict(start=len(train), end=len(df)-1, exog=test.iloc[:, exog_cols])
                mape_arimax = mean_absolute_percentage_error(test.iloc[:, 1], predictions_arimax)
                print(f"Sheet '{sheet_name}': ARIMAX MAPE = {mape_arimax}")
                if sheet_name not in results:
                    results[sheet_name] = {}
                results[sheet_name]['ARIMAX'] = mape_arimax
                # print(exog_cols)
            except Exception as e:
                print(f"Error fitting ARIMAX model for sheet '{sheet_name}': {e}")

        except KeyError:
            print(f"DataFrame '{sheet_name}' not found. Skipping.")
        except Exception as e:
            print(f"An error occurred while processing sheet '{sheet_name}': {e}")
    return results

# results = generate_results(relevant_sheet_names)

app = Flask(__name__)

@app.route("/")
def home():
  """
  Health check endpoint.

  Returns:
      dict: A dictionary containing the status of the application.
            Example: {"status": "Ok!"}
  """
  return {"status": "Ok!"}


@app.route("/get_map_value")
def get_map_value():
    """
    Endpoint to trigger data fetching and analysis.

    This endpoint calls `create_data_frame` to fetch data and `generate_results`
    to perform the analysis. It returns the calculated MAPE scores for each sheet.

    Returns:
        dict: A dictionary containing the analysis results (MAPE scores).
    """
    relevant_sheet_names = create_data_frame()
    results = generate_results(relevant_sheet_names)
    return results

if __name__ == "__main__":
    app.run()
