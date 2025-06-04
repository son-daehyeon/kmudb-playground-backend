import sqlparse
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_playground_db
from app.deps.auth import get_current_user
from app.utils.response import api_response
from app.utils.serialize import row_to_jsonable_array

router = APIRouter()


def validate_query(query):
    if not query:
        raise HTTPException(status_code=400, detail="쿼리를 입력해주세요.")

    statements = [s for s in sqlparse.parse(query) if str(s).strip()]
    if len(statements) != 1:
        raise HTTPException(
            status_code=400,
            detail="단일 쿼리만 허용됩니다."
        )
    stmt = statements[0]
    first_token = next((t for t in stmt.tokens if not t.is_whitespace), None)

    if first_token is None or first_token.normalized.upper() not in ("SELECT", "WITH"):
        raise HTTPException(
            status_code=400,
            detail="읽기 전용 쿼리만 허용됩니다."
        )

    return str(stmt).strip()


@router.post("/execute")
def execute_query(
        payload: dict = Body(...),
        _=Depends(get_current_user),
        playground_db: Session = Depends(get_playground_db)
):
    query = validate_query(payload.get("query"))

    result = playground_db.execute(text(query))

    columns = list(result.keys())
    rows = [row_to_jsonable_array(row, columns) for row in result.fetchall()]

    return api_response({
        "columns": columns,
        "result": rows
    })
