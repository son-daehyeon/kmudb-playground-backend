def row_to_jsonable(row):
    import datetime
    from decimal import Decimal
    import uuid
    from pathlib import Path
    from enum import Enum
    import base64

    def convert(v):
        if isinstance(v, (datetime.datetime, datetime.date, datetime.time)):
            return v.isoformat()
        elif isinstance(v, Decimal):
            return float(v)
        elif isinstance(v, uuid.UUID):
            return str(v)
        elif isinstance(v, (bytes, bytearray)):
            # base64 인코딩 (혹은 str(v) 가능)
            return base64.b64encode(v).decode('utf-8')
        elif isinstance(v, (set, frozenset)):
            return list(v)
        elif isinstance(v, Path):
            return str(v)
        elif isinstance(v, Enum):
            return v.value
        else:
            return v

    return {k: convert(v) for k, v in dict(row).items()}
