# Currency Exchange API

A RESTful Currency Exchange API built with **FastAPI** and powered by [AllRatesToday](https://allratestoday.com). It provides live exchange rates, historical exchange rates, advanced rate queries, and supported currency information.

The project uses AllRatesToday as its data provider and does not require a database.

## Features

- Get live currency exchange rates.
- Retrieve historical exchange rates.
- Query advanced exchange-rate data using dates and timestamps.
- Convert currency amounts.
- Retrieve a list of all supported currencies.
- Download responses in JSON, CSV, XML, and XLSX formats where supported.
- Secure API key management using environment variables.
- Asynchronous HTTP requests using HTTPX.
- Interactive API documentation using Swagger UI.
- Modular and maintainable project architecture.

## Tech Stack

- **Python**
- **FastAPI** – REST API framework.
- **Uvicorn** – ASGI server.
- **HTTPX** – Asynchronous HTTP client.
- **Python Dotenv** – Environment variable management.
- **AllRatesToday API** – Currency exchange-rate data provider.

## Project Structure

```text
currency-exchange-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── rates.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── allrates.py
│   │
│   └── config.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mdmuneeb/PSEB-Assignement-1
```

Navigate into the project directory:

```bash
cd currency-exchange-api
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
ALLRATES_API_KEY=your_actual_api_key
```

Get your API key from [AllRatesToday](https://allratestoday.com).

**Note:** The `/symbols` endpoint does not require authentication. All other endpoints use the API key.

### 5. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically generates interactive API documentation.

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Available Endpoints

### 1. Get Live Exchange Rate

**Endpoint:**

```http
GET /rate
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| source | string | Yes | Base currency code |
| target | string | Yes | Target currency code |

**Example:**

```http
GET /rate?source=USD&target=EUR
```

### 2. Get Historical Exchange Rates

**Endpoint:**

```http
GET /historical-rates
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| source | string | Yes | Base currency code |
| target | string | Yes | Target currency code |
| period | string | No | `1d`, `7d`, `30d`, or `1y` |
| format | string | No | `json`, `csv`, `xml`, or `xlsx` |

**Example:**

```http
GET /historical-rates?source=USD&target=EUR&period=7d
```

**Example with CSV:**

```http
GET /historical-rates?source=USD&target=EUR&period=30d&format=csv
```

### 3. Get Advanced Exchange Rates

**Endpoint:**

```http
GET /v1/rates
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| source | string | No | Base currency code |
| target | string | No | Target currency code(s), comma-separated |
| time | datetime | No | Retrieve rates for a specific timestamp |
| from | date | No | Start date |
| to | date | No | End date (exclusive) |
| group | string | No | `minute`, `hour`, or `day` |
| format | string | No | `json`, `csv`, `xml`, or `xlsx` |
| amount | float | No | Amount to convert; requires one source and one target |

**Examples:**

Get rates for USD to EUR:

```http
GET /v1/rates?source=USD&target=EUR
```

Get rates for multiple currencies:

```http
GET /v1/rates?source=USD&target=EUR,GBP,PKR
```

Get rates for a specific date:

```http
GET /v1/rates?source=USD&target=EUR&time=2026-11-18T12:00:00
```

Get historical rates between dates:

```http
GET /v1/rates?source=USD&target=EUR&from=2026-11-01&to=2026-11-18&group=day
```

Convert a specific amount:

```http
GET /v1/rates?source=USD&target=PKR&amount=100
```

Get results in Excel format:

```http
GET /v1/rates?source=USD&target=EUR&format=xlsx
```

**Important:**
- Both `from` and `to` must be provided together.
- The `to` date is exclusive.
- Use either `time` or the `from`/`to` date range.
- The `group` parameter can only be used with a date range.
- Amount conversion requires exactly one source and one target currency.

### 4. Get Supported Currencies

**Endpoint:**

```http
GET /symbols
```

Returns all supported currency codes, names, and symbols.

This endpoint does not require authentication and does not count toward the AllRatesToday monthly API quota.

**Query Parameters:**

| Parameter | Type | Required | Description |
|---|---|---|---|
| format | string | No | `json`, `csv`, `xml`, or `xlsx` |

**Examples:**

Get supported currencies in JSON:

```http
GET /symbols
```

Get supported currencies in CSV:

```http
GET /symbols?format=csv
```

Get supported currencies in Excel:

```http
GET /symbols?format=xlsx
```

**Example Response:**

```json
{
  "currencies": [
    {
      "code": "USD",
      "name": "US Dollar",
      "symbol": "$"
    }
  ],
  "count": 161
}
```

## Error Handling

The API handles common errors and returns appropriate HTTP status codes.

| Status Code | Description |
|---|---|
| 200 | Request successful |
| 400 | Invalid request parameters |
| 401 | Authentication failed |
| 429 | API monthly quota exceeded |
| 500 | Internal server or configuration error |
| 502 | Unable to connect to the upstream API |
| 504 | Upstream API request timeout |

## Security

- Store your API key in the `.env` file.
- Never commit your `.env` file to GitHub.
- Use environment variables for sensitive configuration.
- Keep your API key private.

Ensure your `.gitignore` contains:

```gitignore
.env
__pycache__/
*.py[cod]
.venv/
venv/
```

## Running Without Reload

For production environments, run the application without the development reload option:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For production deployments, configure your hosting environment with the required `ALLRATES_API_KEY` environment variable.

## Data Provider

Exchange-rate data is provided by [AllRatesToday](https://allratestoday.com).

Refer to the provider's documentation for API usage, supported currencies, response formats, and quota information.

## License

This project is open source. Add a license file (such as MIT) if you intend to distribute it under that license.
