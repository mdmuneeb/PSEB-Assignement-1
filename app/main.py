
import os

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import date, datetime
from typing import Optional
from fastapi import Query

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


@app.get("/v1/rates")
async def get_rates(
    source: Optional[str] = Query(default=None, min_length=3, max_length=3),
    target: Optional[str] = Query(default=None),
    time: Optional[datetime] = Query(default=None),
    from_date: Optional[date] = Query(default=None, alias="from"),
    to_date: Optional[date] = Query(default=None, alias="to"),
    group: Optional[str] = Query(
        default=None,
        pattern="^(minute|hour|day)$"
    ),
    format: str = Query(
        default="json",
        pattern="^(json|csv|xml|xlsx)$"
    ),
    amount: Optional[float] = Query(default=None, ge=0),
):
    """
    Get live or historical currency exchange rates.

    Supports multiple target currencies, historical dates,
    time series, and amount conversion.
    """

    if not ALLRATES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AllRatesToday API key is not configured.",
        )

    # Validate historical date range.
    if (from_date is None) != (to_date is None):
        raise HTTPException(
            status_code=400,
            detail="Both 'from' and 'to' parameters must be provided together.",
        )

    if from_date and to_date and from_date >= to_date:
        raise HTTPException(
            status_code=400,
            detail="'from' must be earlier than 'to'.",
        )

    if time is not None and from_date is not None:
        raise HTTPException(
            status_code=400,
            detail="Use either 'time' or 'from'/'to', not both.",
        )

    # Amount conversion requires exactly one source and one target.
    if amount is not None:
        if not source or not target or "," in target:
            raise HTTPException(
                status_code=400,
                detail="Amount conversion requires exactly one source and one target currency.",
            )

    url = f"{ALLRATES_BASE_URL}/v1/rates"

    headers = {
        "Authorization": f"Bearer {ALLRATES_API_KEY}"
    }

    params = {}

    if source:
        params["source"] = source.upper()

    if target:
        params["target"] = target.upper()

    if time:
        params["time"] = time.isoformat()

    if from_date:
        params["from"] = from_date.isoformat()

    if to_date:
        params["to"] = to_date.isoformat()

    if group:
        params["group"] = group

    if format:
        params["format"] = format

    if amount is not None:
        params["amount"] = amount

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

        # Return JSON as a Python JSON response.
        if format == "json":
            return response.json()

        # Preserve original file content for other formats.
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
                    f"attachment; filename=rates.{format}",
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
