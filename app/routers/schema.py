from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_playground_db
from app.deps.auth import get_current_user
from app.utils.response import api_response

router = APIRouter()


@router.get("/schema")
def get_schema(_=Depends(get_current_user), playground_db: Session = Depends(get_playground_db)):
    # noinspection SqlDialectInspection
    schema_query = """
                   SELECT c.table_name, c.column_name, c.column_type, c.is_nullable
                   FROM information_schema.columns c
                            JOIN information_schema.tables t
                                 ON c.table_schema = t.table_schema AND c.table_name = t.table_name
                   WHERE c.table_schema = DATABASE()
                     AND t.table_type = 'BASE TABLE'
                   ORDER BY c.table_name, c.ordinal_position;
                   """
    schema_result = playground_db.execute(text(schema_query))
    schema_info = {}
    for row in schema_result.fetchall():
        table = row._mapping['TABLE_NAME']
        col = {
            'column_name': row._mapping['COLUMN_NAME'],
            'column_type': row._mapping['COLUMN_TYPE'],
            'is_nullable': row._mapping['IS_NULLABLE'] == 'YES'
        }
        schema_info.setdefault(table, []).append(col)

    # noinspection SqlDialectInspection
    fk_query = """
               SELECT k.table_name, k.column_name, k.referenced_table_name, k.referenced_column_name
               FROM information_schema.KEY_COLUMN_USAGE k
                        JOIN information_schema.tables t
                             ON k.table_schema = t.table_schema
                                 AND k.table_name = t.table_name
               WHERE k.table_schema = DATABASE()
                 AND k.referenced_table_name IS NOT NULL
                 AND t.table_type = 'BASE TABLE';
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

    # noinspection SqlDialectInspection
    pk_query = """
               SELECT k.table_name, k.column_name
               FROM information_schema.KEY_COLUMN_USAGE k
                        JOIN information_schema.tables t
                             ON k.table_schema = t.table_schema
                                 AND k.table_name = t.table_name
               WHERE k.table_schema = DATABASE()
                 AND k.constraint_name = 'PRIMARY'
                 AND t.table_type = 'BASE TABLE'
               ORDER BY k.table_name, k.ordinal_position;
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
