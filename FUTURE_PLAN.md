# Future Plan (Phase 2)

This document outlines the planned enhancements and features for Phase 2 of the Time Series Analysis application. Phase 1 focused on establishing the core functionality and documentation.

## 1. Code Quality & Refactoring

*   **Remove Global Variables**:
    *   *Current State*: `create_data_frame` stores DataFrames in `globals()`.
    *   *Plan*: Refactor `create_data_frame` to return a dictionary of DataFrames (`{sheet_name: dataframe}`) and pass this dictionary to `generate_results`.
*   **Parameterization**:
    *   *Current State*: The Spreadsheet ID is hardcoded (`1jnTFKyRtwLc1cK1YXQ3GER_z8dYmpsj0VmB9nih-szQ`).
    *   *Plan*: Move the Spreadsheet ID to an environment variable (e.g., `SPREADSHEET_ID`) or a configuration file.
*   **Type Hinting**:
    *   Add Python type hints to all functions to improve code readability and static analysis.

## 2. Robustness & Error Handling

*   **Improved Logging**:
    *   Replace `print()` statements with the standard `logging` module. This will allow for better control over log levels (INFO, ERROR, DEBUG) and log formatting.
*   **Exception Handling**:
    *   Refine `try-except` blocks to catch specific exceptions rather than generic `Exception`.
    *   Implement a mechanism to return partial results if some sheets fail, while clearly indicating which ones failed.

## 3. Testing

*   **Unit Tests**:
    *   Create a `tests/` directory.
    *   Write unit tests for data transformation logic using `pytest`.
    *   Mock external dependencies (`gspread`, `google.auth`) to test the application logic in isolation without needing actual Google Sheets access.
*   **Integration Tests**:
    *   Create integration tests to verify the full flow from data ingestion (using a test spreadsheet) to result generation.

## 4. Features

*   **Model Selection**:
    *   Allow the user to specify model parameters (e.g., ARIMA order) via query parameters in the API request.
*   **Data Persistence**:
    *   Cache fetched data or model results (e.g., using Redis) to reduce API calls to Google Sheets and speed up response times.
*   **Visualization**:
    *   Add an endpoint to generate plots of the forecasts and return them (e.g., as base64 encoded images or URLs).

## 5. Deployment

*   **Dockerization**:
    *   Create a `Dockerfile` to containerize the application.
    *   Add a `docker-compose.yml` for easy local development.
*   **CI/CD**:
    *   Set up a CI/CD pipeline (e.g., GitHub Actions) to run tests and linting on every commit.
