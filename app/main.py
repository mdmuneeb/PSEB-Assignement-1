
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI(
    title="Currency Exchange API",
    description="Backend API for live currency exchange rates",
    version="1.0.0",
)

ALLRATES_BASE_URL = "https://allratestoday.com/api"
ALLRATES_API_KEY = os.getenv("ALLRATES_API_KEY")


@app.get("/rate")
async def get_exchange_rate(
    source: str = Query(..., min_length=3, max_length=3),
    target: str = Query(..., min_length=3, max_length=3),
):
    """
    Get the current exchange rate between two currencies.
    Example: /rate?source=USD&target=EUR
    """

    if not ALLRATES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AllRatesToday API key is not configured.",
        )

    url = f"{ALLRATES_BASE_URL}/rate"

    headers = {
        "Authorization": f"Bearer {ALLRATES_API_KEY}"
    }

    params = {
        "source": source.upper(),
        "target": target.upper(),
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
            )

        if response.status_code != 200:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {"detail": response.text}

            # Preserve useful monthly usage information.
            forwarded_headers = {
                key: response.headers[key]
                for key in [
                    "X-Monthly-Limit",
                    "X-Monthly-Used",
                    "X-Monthly-Resets",
                ]
                if key in response.headers
            }

            return JSONResponse(
                status_code=response.status_code,
                content=error_data,
                headers=forwarded_headers,
            )

        return response.json()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AllRatesToday API request timed out.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to AllRatesToday API.",
        )




@app.get("/historical-rates")
async def get_historical_rates(
    source: str = Query(..., min_length=3, max_length=3),
    target: str = Query(..., min_length=3, max_length=3),
    period: str = Query(
        default="1d",
        pattern="^(1d|7d|30d|1y)$"
    ),
    format: str = Query(
        default="json",
        pattern="^(json|csv|xml|xlsx)$"
    ),
):
    """
    Get historical exchange rates for a currency pair.

    Supported periods: 1d, 7d, 30d, 1y
    Supported formats: json, csv, xml, xlsx
    """

    if not ALLRATES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AllRatesToday API key is not configured.",
        )

    url = f"{ALLRATES_BASE_URL}/historical-rates"

    headers = {
        "Authorization": f"Bearer {ALLRATES_API_KEY}"
    }

    params = {
        "source": source.upper(),
        "target": target.upper(),
        "period": period,
        "format": format,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
            )

        if response.status_code != 200:
            try:
                error_data = response.json()
            except ValueError:
                error_data = {"detail": response.text}

            forwarded_headers = {
                key: response.headers[key]
                for key in [
                    "X-Monthly-Limit",
                    "X-Monthly-Used",
                    "X-Monthly-Resets",
                ]
                if key in response.headers
            }

            return JSONResponse(
                status_code=response.status_code,
                content=error_data,
                headers=forwarded_headers,
            )

        # JSON response: return parsed JSON.
        if format == "json":
            return response.json()

        # CSV, XML and XLSX: preserve original response bytes.
        from fastapi.responses import Response

        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get(
                "Content-Type",
                "application/octet-stream",
            ),
            headers={
                "Content-Disposition": response.headers.get(
                    "Content-Disposition",
                    f"attachment; filename=historical-rates.{format}",
                )
            },
        )

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="AllRatesToday API request timed out.",
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Unable to connect to AllRatesToday API.",
        )
