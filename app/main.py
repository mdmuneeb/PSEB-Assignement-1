
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
