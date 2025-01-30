import pandas as pd
# from google.colab import auth
import  google.auth
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
  return {"status": "Ok!"}


@app.route("/get_map_value")
def get_map_value():
    relevant_sheet_names = create_data_frame()
    results = generate_results(relevant_sheet_names)
    return results

app.run()