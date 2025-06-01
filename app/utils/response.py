from fastapi.responses import JSONResponse


def api_response(data=None, error=False, message=None):
    return JSONResponse(
        status_code=200,
        content={
            "error": error,
            "message": message,
            "data": data
        }
    )
