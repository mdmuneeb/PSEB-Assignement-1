
import httpx

from fastapi import HTTPException

from app.config import ALLRATES_API_KEY, ALLRATES_BASE_URL


async def make_allrates_request(
    endpoint: str,
    params: dict,
    timeout: float = 30.0,
) -> httpx.Response:
    """
    Send an authenticated request to AllRatesToday.
    """

    if not ALLRATES_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="AllRatesToday API key is not configured.",
        )

    url = f"{ALLRATES_BASE_URL}/{endpoint}"

    headers = {
        "Authorization": f"Bearer {ALLRATES_API_KEY}"
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(
                url,
                headers=headers,
                params={
                    key: value
                    for key, value in params.items()
                    if value is not None
                },
            )

        return response

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


def handle_allrates_response(response: httpx.Response, format: str = "json"):
    """
    Process the upstream response.

    JSON responses are returned as JSON.
    CSV, XML and XLSX responses preserve their original bytes.
    """

    forwarded_headers = {
        key: response.headers[key]
        for key in [
            "X-Monthly-Limit",
            "X-Monthly-Used",
            "X-Monthly-Resets",
        ]
        if key in response.headers
    }

    if response.status_code != 200:
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"detail": response.text}

        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=response.status_code,
            content=error_data,
            headers=forwarded_headers,
        )

    if format == "json":
        from fastapi.responses import JSONResponse

        return JSONResponse(
            content=response.json(),
            headers=forwarded_headers,
        )

    from fastapi.responses import Response

    forwarded_headers["Content-Disposition"] = response.headers.get(
        "Content-Disposition",
        f"attachment; filename=allrates-response.{format}",
    )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get(
            "Content-Type",
            "application/octet-stream",
        ),
        headers=forwarded_headers,
    )
