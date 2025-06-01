import datetime

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    kakao_id = mapped_column(String(100), unique=True, nullable=False)
    nickname = mapped_column(String(100), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), default=datetime.datetime.now)

    submissions = relationship("Submission", back_populates="user")


class Problem(Base):
    __tablename__ = "problems"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    description = mapped_column(String(255), nullable=False)
    query = mapped_column(String(2000), nullable=False)

    submissions = relationship("Submission", back_populates="problem")


class Submission(Base):
    __tablename__ = "submissions"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    problem_id = mapped_column(Integer, ForeignKey('problems.id'), nullable=False)
    query = mapped_column(String(5000), nullable=False)
    submitted_at = mapped_column(DateTime(timezone=True), default=datetime.datetime.now)

    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
