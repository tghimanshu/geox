# Time Series Analysis App

This repository contains a Flask application for performing time series analysis on data stored in Google Sheets. It utilizes ARIMA and ARIMAX models to forecast future values and calculates the Mean Absolute Percentage Error (MAPE) to evaluate model performance.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)

## Overview

The application fetches data from a specified Google Spreadsheet. Each sheet in the spreadsheet (except "Data" and "CorrelationResults") is treated as a separate dataset. The app performs the following steps:

1.  **Data Ingestion**: Reads data from Google Sheets.
2.  **Preprocessing**: Converts columns to numeric types.
3.  **Modeling**:
    *   **ARIMA**: AutoRegressive Integrated Moving Average.
    *   **ARIMAX**: ARIMA with eXogenous regressors.
4.  **Evaluation**: Calculates MAPE on a held-out test set (last 30 data points).
5.  **Reporting**: Returns the MAPE scores via a JSON API.

## Prerequisites

*   Python 3.7+
*   A Google Cloud Platform (GCP) Service Account with access to the target Google Sheet.
*   The Google Sheet ID is currently hardcoded in `app.py`. You will need access to the sheet with ID `1jnTFKyRtwLc1cK1YXQ3GER_z8dYmpsj0VmB9nih-szQ` or modify the code to use your own.

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application requires Google Cloud credentials to be provided via an environment variable.

1.  **GCP Credentials**:
    *   Obtain your service account key file (JSON format).
    *   Base64 encode the content of the JSON key file.
    *   Set the `GCP_CREDS` environment variable with the base64 encoded string.

    **Example (Linux/macOS):**
    ```bash
    export GCP_CREDS=$(base64 -w 0 path/to/service-account.json)
    ```

    **Example (Windows PowerShell):**
    ```powershell
    $creds = Get-Content path\to\service-account.json -Raw
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($creds)
    $encoded = [System.Convert]::ToBase64String($bytes)
    $env:GCP_CREDS = $encoded
    ```

## Usage

Start the Flask application:

```bash
python app.py
```

The application will start on the default Flask port (usually 5000).

## API Endpoints

### `GET /`

Health check endpoint.

**Response:**
```json
{
  "status": "Ok!"
}
```

### `GET /get_map_value`

Triggers the analysis process.

1.  Fetches data from the Google Sheet.
2.  Trains ARIMA and ARIMAX models.
3.  Calculates MAPE.
4.  Returns the results.

**Response Example:**
```json
{
  "Sheet1": {
    "ARIMA": 0.052,
    "ARIMAX": 0.048
  },
  "Sheet2": {
    "ARIMA": 0.12,
    "ARIMAX": 0.11
  }
}
```

## Contributing

Please refer to `FUTURE_PLAN.md` for the roadmap and future enhancements.
