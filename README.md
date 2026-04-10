# FirstCoursework

A Python project for analyzing financial transactions, including event generation, reports, and search services.

## Features

- **Events Page**
  - Generates a JSON response with expenses, income, currency rates, and stock prices.

- **Reports**
  - Spending by category for the last 3 months.
  - Automatic saving of report results to a file via decorator.

- **Services**
  - Search transactions containing phone numbers using regex.

## Tech Stack

- Python 3.11+
- pandas
- requests
- pytest
- logging
- dotenv

## Project Structure

- src/ # main application logic
- tests/ # test suite
- data/ # input and generated data


## Setup

```bash
poetry install
```
## Run

```bash
poetry run pithon main.py
```
## Testing

```bash
poetry run pytest
```

 
## Environment Variables

Create a .env file based on .env.example:

EXCHANGE_API_KEY=your_api_key

## Notes
API keys are stored securely in .env
Generated report files are ignored via .gitignore