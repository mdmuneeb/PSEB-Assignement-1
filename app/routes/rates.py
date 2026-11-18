
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.allrates import (
    make_allrates_request,
    handle_allrates_response,
)

router = APIRouter(tags=["Exchange Rates"])


# --------------------------------------------------
# 1. Current Exchange Rate
# GET /rate
# --------------------------------------------------

@router.get("/rate")
async def get_exchange_rate(
    source: str = Query(..., min_length=3, max_length=3),
    target: str = Query(..., min_length=3, max_length=3),
):
    params = {
        "source": source.upper(),
        "target": target.upper(),
    }

    response = await make_allrates_request(
        endpoint="rate",
        params=params,
        timeout=15.0,
    )

    return handle_allrates_response(response)


# --------------------------------------------------
# 2. Historical Exchange Rates
# GET /historical-rates
# --------------------------------------------------

@router.get("/historical-rates")
async def get_historical_rates(
    source: str = Query(..., min_length=3, max_length=3),
    target: str = Query(..., min_length=3, max_length=3),
    period: str = Query(
        default="1d",
        pattern="^(1d|7d|30d|1y)$",
    ),
    format: str = Query(
        default="json",
        pattern="^(json|csv|xml|xlsx)$",
    ),
):
    params = {
        "source": source.upper(),
        "target": target.upper(),
        "period": period,
        "format": format,
    }

    response = await make_allrates_request(
        endpoint="historical-rates",
        params=params,
    )

    return handle_allrates_response(response, format)


# --------------------------------------------------
# 3. Wise-compatible Rates
# GET /v1/rates
# --------------------------------------------------

@router.get("/v1/rates")
async def get_rates(
    source: Optional[str] = Query(
        default=None,
        min_length=3,
        max_length=3,
    ),
    target: Optional[str] = Query(default=None),
    time: Optional[datetime] = Query(default=None),
    from_date: Optional[date] = Query(default=None, alias="from"),
    to_date: Optional[date] = Query(default=None, alias="to"),
    group: Optional[str] = Query(
        default=None,
        pattern="^(minute|hour|day)$",
    ),
    format: str = Query(
        default="json",
        pattern="^(json|csv|xml|xlsx)$",
    ),
    amount: Optional[float] = Query(default=None, ge=0),
):
    # Validate date range parameters.
    if (from_date is None) != (to_date is None):
        raise HTTPException(
            status_code=400,
            detail="Both 'from' and 'to' parameters are required together.",
        )

    if from_date and to_date and from_date >= to_date:
        raise HTTPException(
            status_code=400,
            detail="'from' must be earlier than 'to'.",
        )

    if time and from_date:
        raise HTTPException(
            status_code=400,
            detail="Use either 'time' or 'from'/'to', not both.",
        )

    if group and not from_date:
        raise HTTPException(
            status_code=400,
            detail="'group' can only be used with 'from' and 'to'.",
        )

    # Amount conversion requires one source and one target.
    if amount is not None:
        if not source or not target or "," in target:
            raise HTTPException(
                status_code=400,
                detail="Amount conversion requires exactly one source and one target.",
            )

    params = {
        "source": source.upper() if source else None,
        "target": ",".join(
            currency.strip().upper()
            for currency in target.split(",")
        ) if target else None,
        "time": time.isoformat() if time else None,
        "from": from_date.isoformat() if from_date else None,
        "to": to_date.isoformat() if to_date else None,
        "group": group,
        "format": format,
        "amount": amount,
    }

    response = await make_allrates_request(
        endpoint="v1/rates",
        params=params,
    )

    return handle_allrates_response(response, format)
