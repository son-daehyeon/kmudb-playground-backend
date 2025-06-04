from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db, get_playground_db
from app.deps.auth import get_current_user
from app.models import Problem, Submission
from app.routers.execute import validate_query
from app.utils.response import api_response
from app.utils.serialize import row_to_jsonable_array

router = APIRouter()


@router.get("/problems")
def get_problems(user=Depends(get_current_user), db: Session = Depends(get_db)):
    problems = db.query(Problem).all()

    solved = set(
        row[0]
        for row in db.query(Submission.problem_id).filter(Submission.user_id == user.id).distinct().all()
    )

    return api_response({
        'problems': [
            {
                "id": p.id,
                "solved": p.id in solved
            }
            for p in problems
        ]
    })


@router.get("/problems/{problem_id}")
def get_problem(problem_id: int,
                user=Depends(get_current_user),
                db: Session = Depends(get_db),
                playground_db: Session = Depends(get_playground_db)):
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    last_query = (
        db.query(Submission)
        .filter(Submission.user_id == user.id, Submission.problem_id == problem_id)
        .order_by(Submission.submitted_at.desc())
        .first()
    )

    if last_query:
        solved = True
        query = last_query.query
    else:
        solved = False
        query = None

    result = playground_db.execute(text(problem.query))

    columns = list(result.keys())
    rows = [row_to_jsonable_array(row, columns) for row in result.fetchmany(3)]

    return api_response({
        "id": problem.id,
        "description": problem.description,
        "solved": solved,
        "query": query,
        "example": {
            "columns": columns,
            "result": rows
        }
    })


@router.post("/problems/{problem_id}")
def submit(
        problem_id: int,
        payload: dict = Body(...),
        user=Depends(get_current_user),
        db: Session = Depends(get_db),
        playground_db: Session = Depends(get_playground_db)
):
    query = validate_query(payload.get("query"))

    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="문제를 찾을 수 없습니다.")

    user_result = playground_db.execute(text(query))
    user_rows = [dict(row) for row in user_result.mappings().fetchall()]

    answer_result = playground_db.execute(text(problem.query))
    answer_rows = [dict(row) for row in answer_result.mappings().fetchall()]

    is_correct = (user_rows == answer_rows)

    if is_correct:
        submission = Submission(
            user_id=user.id,
            problem_id=problem.id,
            query=query
        )
        db.add(submission)
        db.commit()

    return api_response({"correct": is_correct})
