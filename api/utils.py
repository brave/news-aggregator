from fastapi import HTTPException, Request, status

from config import get_config

config = get_config()

ep_err_msg = (
    "Requested endpoint not found. The endpoint you are accessing is not available. "
    "Please check your API request."
)

ep_input_miss_err_msg = "The server could not understand the request due to syntax or other client-side errors."


async def request_auth(request: Request):
    details = f"Unauthorized access attempt detected: Bearer token invalid or missing. Access denied."
    try:
        if (
            request.headers.get("authorization")
            != f"Bearer {config.news_data_api_token}"
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=details
            )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=details)


def get_db():
    try:
        with config.get_db_session() as session:
            yield session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
