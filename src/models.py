"""
Created by Alejandro Cuevas
(t-alejandroc@microsoft.com / acuevasv@andrew.cmu.edu)
August 2023
"""


from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(50), nullable=False)
    study_group = db.Column(db.String(50), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    participant_id = db.Column(db.String(50), nullable=False)

    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    category = db.Column(db.String(50), nullable=True)
    question_order = db.Column(db.Integer, nullable=True)
    origin = db.Column(db.String(50), nullable=False)

    chatlog_id = db.Column(db.Integer, nullable=False)


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    question_id = db.Column(db.Integer, nullable=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    chatlog_id = db.Column(db.Integer, nullable=False)


class ChatLogLookup(db.Model):
    __tablename__ = "chat_log_lookup"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    participant_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )


class ChatLog(db.Model):
    __tablename__ = "chat_logs"

    id = db.Column(db.Integer, primary_key=True)
    chatlog_id = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    participant_id = db.Column(db.String(50), nullable=True)
    question_id = db.Column(db.Integer, nullable=True)
    answer_id = db.Column(db.Integer, nullable=True)
    body = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )


class AIResponse(db.Model):
    __tablename__ = "ai_responses"

    id = db.Column(db.Integer, primary_key=True)
    chatlog_id = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    model_parameters = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )


class AIModel:
    def __init__(self, model_name, kernel, skill):
        self.role = model_name
        self.context = kernel.create_new_context()
        self.skill = skill
