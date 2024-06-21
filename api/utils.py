from fastapi import HTTPException, Request, status

from config import get_config

config = get_config()

ep_err_msg = (
    "Requested endpoint not found. The endpoint you are accessing is not available. "
    "Please check your API request."
)

ep_input_miss_err_msg = "The server could not understand the request due to syntax or other client-side errors."


async def request_auth(request: Request):
    try:
        auth_header = request.headers.get("authorization")
        if auth_header is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing.",
            )

        if auth_header != f"Bearer {config.news_data_api_token}":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token invalid."
            )

    except KeyError as ke:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Header key error: {str(ke)}",
        )
    except TypeError as te:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Type error: {str(te)}"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


def get_db():
    try:
        with config.get_db_session() as session:
            yield session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
