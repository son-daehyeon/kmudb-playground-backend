if __name__ == "__main__":
    from app.database import engine, Base
    from app.models import User, Problem, Submission

    # noinspection PyStatementEffect
    (User, Problem, Submission)

    Base.metadata.create_all(engine)
