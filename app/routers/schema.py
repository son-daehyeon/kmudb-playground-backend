from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_playground_db
from app.deps.auth import get_current_user
from app.utils.response import api_response

router = APIRouter()


@router.get("/schema")
def get_schema(_=Depends(get_current_user), playground_db: Session = Depends(get_playground_db)):
    schema_query = """
                   SELECT table_name, column_name, data_type
                   FROM information_schema.columns
                   WHERE table_schema = DATABASE()
                   ORDER BY table_name, ordinal_position;
                   """
    schema_result = playground_db.execute(text(schema_query))
    schema_info = {}
    for row in schema_result.fetchall():
        table = row._mapping['TABLE_NAME']
        col = {
            'column_name': row._mapping['COLUMN_NAME'],
            'data_type': row._mapping['DATA_TYPE']
        }
        schema_info.setdefault(table, []).append(col)

    fk_query = """
               SELECT table_name, column_name, referenced_table_name, referenced_column_name
               FROM information_schema.KEY_COLUMN_USAGE
               WHERE table_schema = DATABASE()
                 AND referenced_table_name IS NOT NULL;
               """
    fk_result = playground_db.execute(text(fk_query))
    relations = []
    for row in fk_result.fetchall():
        relations.append({
            "table_name": row._mapping['TABLE_NAME'],
            "column_name": row._mapping['COLUMN_NAME'],
            "referenced_table_name": row._mapping['REFERENCED_TABLE_NAME'],
            "referenced_column_name": row._mapping['REFERENCED_COLUMN_NAME'],
        })

    pk_query = """
               SELECT table_name, column_name
               FROM information_schema.KEY_COLUMN_USAGE
               WHERE table_schema = DATABASE()
                 AND constraint_name = 'PRIMARY'
               ORDER BY table_name, ordinal_position;
               """
    pk_result = playground_db.execute(text(pk_query))
    pk_info = {}
    for row in pk_result.fetchall():
        table = row._mapping['TABLE_NAME']
        col = row._mapping['COLUMN_NAME']
        pk_info.setdefault(table, []).append(col)

    return api_response({
        "schema": schema_info,
        "relations": relations,
        "primary_keys": pk_info
    })
