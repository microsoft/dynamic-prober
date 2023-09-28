"""
Created by Alejandro Cuevas
(t-alejandroc@microsoft.com / acuevasv@andrew.cmu.edu)
August 2023
"""

from flask import Flask, render_template, request, session
from flask_cors import CORS
from flask import redirect, url_for
from urllib.parse import quote_plus
from flask_session import Session

import random
import json
import asyncio
from dotenv import load_dotenv
import os

from skills import (
    get_module_response,
    prober_depersonalized,
    global_active_listener,
)

from prompts import PROBER_PROMPT_DEPERSONALIZED_FEWSHOT, ACTIVE_LISTENER_GLOBAL

import utils
from models import db, User, Question, Answer, ChatLog, AIResponse, ChatLogLookup

from question_bank import QUESTIONNAIRE

load_dotenv()
## GLOBALS START ##
LOCAL_DB = os.environ.get("LOCAL_DB")
LOCAL_DB = True if LOCAL_DB == "True" else False
BASELINE_FOLLOWUPS = ["Can you elaborate?", "Can you provide an example?"]
ACTIVE_LISTENER_FIRST_TRANSITION = "Thank you for sharing. I'm glad I got to learn more about you, I'm going to start with the first question."
ACTIVE_LISTENER_NEXT_TRANSITION = (
    "Thank you for your insights. I'm going to ask you about a different value now."
)
API_RETRIES = 3
API_RETRY_DELAY = 5
API_RETRY_ERROR_MSG = (
    "It seems like we are having issues with API connectivity. I apologize for that. "
)
HARDCODED_PARAMS_PROBER = "gpt-3.5-turbo;max_tokens=300;temperature=0.5"
HARDCODED_PARAMS_ACTIVE_LISTENER = "gpt-3.5-turbo;max_tokens=2000;temperature=0"
PROBER_PROMPT_DEPERSONALIZED_FEWSHOT = (
    PROBER_PROMPT_DEPERSONALIZED_FEWSHOT.replace("{", "")
    .replace("}", "")
    .replace("$", "")
)
ACTIVE_LISTENER_GLOBAL = (
    ACTIVE_LISTENER_GLOBAL.replace("{", "").replace("}", "").replace("$", "")
)
END_OF_STUDY_ERROR_MSG = "Sorry, it seems like we are experiencing technical issues. If you'd like to retry, please refresh the page. Please note that you will have to start from the beginning. If you'd like to stop, please close the window and input the code: 19420 in the Qualtrics page."
## GLOBALS END ##

(
    DB_PASSWORD,
    DB_SERVER,
    DB_USERNAME,
    DB_DRIVER,
    DB_DATABASE,
    DB_SECRET,
) = utils.get_db_credentials()

assert DB_PASSWORD is not None
assert DB_SERVER is not None
assert DB_USERNAME is not None
assert DB_DRIVER is not None
assert DB_DATABASE is not None
assert DB_SECRET is not None

app = Flask(__name__)
CORS(app)
Session(app)

logger = utils.setup_logger(__name__)


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = DB_SECRET

    if LOCAL_DB:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    else:
        server = DB_SERVER
        database = DB_DATABASE
        username = DB_USERNAME
        # Need to escape characters for the URI
        password = quote_plus(DB_PASSWORD)
        driver = DB_DRIVER

        logger.info("Connecting to database...")
        logger.info("Server: {}".format(server))
        logger.info("Database: {}".format(database))
        logger.info("Username: {}".format(username))
        logger.info("Driver: {}".format(driver))

        # Using pymssql because pyodbc needed a .so file that didn't exist in the container
        conn_uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
        app.config["SQLALCHEMY_DATABASE_URI"] = conn_uri

    db.init_app(app)
    CORS(app)

    with app.app_context():
        pass

    return app


app = create_app()


@app.route("/init_db")
def init_db():
    with app.app_context():
        logger.info("Creating database...")
        db.create_all()
    return redirect(url_for("index"))


def add_answer_to_db(text):
    answer = Answer()
    answer.body = text
    answer.user_id = session["USER_ID"]
    answer.participant_id = session["PARTICIPANT_ID"]
    answer.question_id = session["QUESTION_ID"]
    answer.chatlog_id = session["CHATLOG_ID"]
    db.session.add(answer)
    db.session.commit()

    logger.debug(
        "CHATLOG_ID: {} | PARTICIPANT ID: {} | Added answer to DB | answer_id: {}".format(
            session["CHATLOG_ID"], session["PARTICIPANT_ID"], answer.id
        )
    )

    return answer.id


def add_question_to_db(text, category, question_order, origin):
    question = Question()
    question.question_order = question_order
    question.origin = origin
    question.participant_id = session["PARTICIPANT_ID"]
    question.user_id = session["USER_ID"]
    question.body = text
    question.category = category
    question.chatlog_id = session["CHATLOG_ID"]

    db.session.add(question)
    db.session.commit()

    logger.debug(
        "CHATLOG_ID: {} | PARTICIPANT ID: {} | Added question to DB | question_id: {}".format(
            session["CHATLOG_ID"], session["PARTICIPANT_ID"], question.id
        )
    )

    return question.id


def add_text_to_chatlog(text, origin):
    chatlog = ChatLog()
    chatlog.chatlog_id = session["CHATLOG_ID"]
    chatlog.body = text
    chatlog.question_id = session["QUESTION_ID"]
    chatlog.answer_id = session["ANSWER_ID"]
    chatlog.participant_id = session["PARTICIPANT_ID"]
    chatlog.user_id = session["USER_ID"]

    db.session.add(chatlog)
    db.session.commit()

    session["CHATLOG"].append("{}: {}".format(origin, text))

    logger.debug(
        "CHATLOG_ID: {} | PARTICIPANT ID: {} | Added text to chatlog: {}".format(
            session["CHATLOG_ID"], session["PARTICIPANT_ID"], text
        )
    )

    return session["CHATLOG_ID"]


def add_ai_response(json_response, model_type):
    global HARDCODED_PARAMS_ACTIVE_LISTENER
    global HARDCODED_PARAMS_PROBER

    if model_type == "prober":
        prompt = PROBER_PROMPT_DEPERSONALIZED_FEWSHOT
        model_parameters = HARDCODED_PARAMS_PROBER
    elif model_type == "active_listener":
        prompt = ACTIVE_LISTENER_GLOBAL
        model_parameters = HARDCODED_PARAMS_ACTIVE_LISTENER
    else:
        prompt = ""
        model_parameters = ""

    ai_response = AIResponse()
    ai_response.response = json_response
    ai_response.chatlog_id = session["CHATLOG_ID"]
    ai_response.model_parameters = model_parameters
    ai_response.prompt = prompt

    db.session.add(ai_response)
    db.session.commit()

    logger.debug(
        "CHATLOG_ID: {} | PARTICIPANT ID: {} | Added model response to DB.".format(
            ai_response.chatlog_id, session["PARTICIPANT_ID"]
        )
    )


@app.route("/")
def index():
    return redirect(url_for("user_landing"))


# Sample URL: http://localhost:5000/user_landing?sg=bs&req=test
# Sample URL: http://localhost:5000/user_landing?sg=dp&req=test
# Sample URL: http://localhost:5000/user_landing?sg=al&req=test
@app.route("/user_landing", methods=["GET"])
def user_landing():
    try:
        study_group = request.args.get("sg")
    except Exception:
        logger.error("No study group provided")
        # Default active listener for testing
        study_group = "al"
    try:
        participant_id = request.args.get("req")
    except Exception:
        logger.error("No participant id provided")
        participant_id = "test"

    study_group = "al" if study_group is None else study_group
    participant_id = "test" if participant_id is None else participant_id

    session["CHAT_HISTORY"] = []
    session["USER_ID"] = None
    session["CHATLOG_ID"] = None
    session["PARTICIPANT_ID"] = participant_id
    session["STUDY_GROUP"] = study_group
    session["QUESTION_ID"] = 0
    session["ANSWER_ID"] = 0
    session["BACKGROUND"] = None
    session["LAST_INPUT"] = ""

    if study_group == "bs":
        session["INTERVIEW_TYPE"] = "BASELINE"
    elif study_group == "dp":
        session["INTERVIEW_TYPE"] = "DYNAMIC_PROBING"
    elif study_group == "al":
        session["INTERVIEW_TYPE"] = "ACTIVE_LISTENER"

    session["INTERACTION_COUNT"] = 0
    session["QUESTIONS_TO_ASK"] = random.sample(list(QUESTIONNAIRE.keys()), 3)
    session["MAIN_QUESTION_COUNT"] = 0
    session["FOLLOWUP_QUESTION_COUNT"] = 0

    session["CHATLOG"] = []
    session["RECENT_CHATLOG"] = []

    # Create a new user entry in the database
    user = User()
    user.study_group = study_group
    user.participant_id = participant_id
    # Save the user entry to the database
    db.session.add(user)
    db.session.commit()

    # Create a new chat log entry for the user
    chatlog = ChatLogLookup()
    chatlog.user_id = user.id
    chatlog.participant_id = participant_id
    db.session.add(chatlog)
    db.session.commit()

    session["USER_ID"] = user.id
    session["CHATLOG_ID"] = chatlog.id

    # Log the user landing
    logger.warning(
        "User landed | participant_id: {}, user_id:{}, study_group: {}".format(
            participant_id, user.id, session["INTERVIEW_TYPE"]
        )
    )
    return render_template("index.html")


def get_chat_history_as_string(recent_only=False):
    if recent_only:
        chatlog = session["RECENT_CHATLOG"]
    else:
        chatlog = session["CHATLOG"]

    return "\n".join(chatlog)


def keep_first_question(input_string):
    # Split the string based on '?' character
    parts = input_string.split("?")

    # If there are multiple '?' characters, keep the first question
    if len(parts) > 1:
        first_question = parts[0] + "?"
    else:
        # If there's only one '?' or none, keep the original string
        first_question = input_string

    return first_question


def engage_prober():
    prober_depersonalized.context["recent_history"] = get_chat_history_as_string(
        recent_only=True
    )
    prober_depersonalized.context["question_of_interest"] = session["CURRENT_QUESTION"]
    json_response = asyncio.run(get_module_response("prober_depersonalized"))
    try:
        json_response = json.loads(json_response.replace("INTERVIEWER ::", "").strip())
        best_response = json_response["question"]
        best_response = keep_first_question(best_response)
        try:
            add_ai_response(json.dumps(json_response), "prober")
        except Exception as e:
            logger.error(
                "CHATLOG_ID: {} | PARTICIPANT ID: {} | Error: {}".format(
                    session["CHATLOG_ID"], session["PARTICIPANT_ID"], e
                )
            )
        return best_response
    except Exception as e:
        logger.error(
            "CHATLOG_ID: {} | PARTICIPANT ID: {} | Prober returned invalid JSON. Error: {}".format(
                session["CHATLOG_ID"], session["PARTICIPANT_ID"], e
            )
        )
        logger.error(json_response)
        return "Sorry, I didn't understand that. Could you rephrase?"


def engage_global_active_listener():
    global_active_listener.context["history"] = get_chat_history_as_string()
    json_response = asyncio.run(get_module_response("global_active_listener"))
    try:
        json_response = json.loads(json_response)
        response = json_response["summary"]
        try:
            add_ai_response(json.dumps(json_response), "global_active_listener")
        except Exception as e:
            logger.error(
                "CHATLOG_ID: {} | PARTICIPANT ID: {} | Error: {}".format(
                    session["CHATLOG_ID"], session["PARTICIPANT_ID"], e
                )
            )
    except Exception:
        logger.error(
            "CHATLOG_ID: {} | PARTICIPANT ID: {} | Global active listener returned invalid JSON".format(
                session["CHATLOG_ID"], session["PARTICIPANT_ID"]
            )
        )
        response = "I wasn't able to summarize our conversation. I apologize."
    return response


def get_background():
    return "To begin, could you tell me a bit about your job position and how knowledgeable you are about AI?"


def get_followup_question():
    if session["INTERVIEW_TYPE"] == "BASELINE":
        response = BASELINE_FOLLOWUPS[session["FOLLOWUP_QUESTION_COUNT"]]
        session["FOLLOWUP_QUESTION_COUNT"] += 1
        return response
    elif session["INTERVIEW_TYPE"] == "DYNAMIC_PROBING":
        response = engage_prober()
        return response
    elif session["INTERVIEW_TYPE"] == "ACTIVE_LISTENER":
        response = engage_prober()
        return response


def get_main_question():
    # Reset the recent chatlog
    session["RECENT_CHATLOG"] = []

    response = QUESTIONNAIRE[
        session["QUESTIONS_TO_ASK"][session["MAIN_QUESTION_COUNT"]]
    ]
    if session["INTERVIEW_TYPE"] == "ACTIVE_LISTENER":
        if session["MAIN_QUESTION_COUNT"] == 0:
            pretext = ACTIVE_LISTENER_FIRST_TRANSITION
        else:
            pretext = ACTIVE_LISTENER_NEXT_TRANSITION
        response = pretext + response
    session["MAIN_QUESTION_COUNT"] += 1
    session["FOLLOWUP_QUESTION_COUNT"] = 0
    session["CURRENT_QUESTION"] = response

    return response


def get_global_active_listener():
    return engage_global_active_listener()


def get_conclusion():
    if session["INTERVIEW_TYPE"] == "ACTIVE_LISTENER":
        pretext = "Thanks for your input, I enjoyed our conversation, and I'm glad I learned more about your views. "
    else:
        pretext = ""
    try:
        if session["USER_ID"] == "test":
            code = 0
        else:
            code = session["USER_ID"]
    except Exception as e:
        logger.error(
            "CHATLOG_ID: {} | PARTICIPANT ID: {} | Error: {}".format(
                session["CHATLOG_ID"], session["PARTICIPANT_ID"], e
            )
        )
        code = 0
    qualtrics_code = str(int(code) + 10000)
    return (
        pretext
        + "Thank you for participating in this study. Please input the following code into the survey: {}.".format(
            qualtrics_code
        )
    )


INTERVIEW_SEQUENCE = {}
INTERVIEW_SEQUENCE["BASELINE"] = [
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_conclusion,
]

INTERVIEW_SEQUENCE["DYNAMIC_PROBING"] = [
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_conclusion,
]

INTERVIEW_SEQUENCE["ACTIVE_LISTENER"] = [
    get_background,
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_main_question,
    get_followup_question,
    get_followup_question,
    get_global_active_listener,
    get_conclusion,
]

# we want to have a function that we can wait on for retry logic
def next_step():
    print(session["INTERACTION_COUNT"])
    if session["INTERACTION_COUNT"] < len(
        INTERVIEW_SEQUENCE[session["INTERVIEW_TYPE"]]
    ):
        return INTERVIEW_SEQUENCE[session["INTERVIEW_TYPE"]][
            session["INTERACTION_COUNT"]
        ]()

    if session["USER_ID"] == "test":
        code = 0
    else:
        code = session["USER_ID"]
    qualtrics_code = str(int(code) + 10000)
    return "The session has concluded. Thank you for your participation. Please input the following code into the survey: {}".format(
        qualtrics_code
    )


def test():
    n = random.randint(0, 10)
    if n < 8:
        raise Exception("test")
    return "test"


@app.route("/chat", methods=["POST"])
def get_data():
    if session["PARTICIPANT_ID"] is None:
        session["PARTICIPANT_ID"] = "test"
    if session["STUDY_GROUP"] is None:
        session["STUDY_GROUP"] = "al"

    data = request.get_json()
    user_input = data.get("data")
    session["ANSWER_ID"] = add_answer_to_db(user_input)
    add_text_to_chatlog(user_input, "USER")

    session["LAST_INPUT"] = user_input
    session["RECENT_CHATLOG"].append("{}: {}".format("USER", user_input))

    # We capture the background
    # The response we want to capture is +1 from the interaction count
    if (
        session["INTERACTION_COUNT"] == 1
        and session["INTERVIEW_TYPE"] == "ACTIVE_LISTENER"
    ):
        session["BACKGROUND"] = user_input
        logger.debug(
            "CHATLOG_ID: {} | PARTICIPANT ID: {} | Background: {}".format(
                session["CHATLOG_ID"], session["PARTICIPANT_ID"], session["BACKGROUND"]
            )
        )
    # We capture the member check response
    if (
        session["INTERACTION_COUNT"] == 12
        and session["INTERVIEW_TYPE"] == "ACTIVE_LISTENER"
    ):
        session["MEMBER_CHECK_ANSWER"] = user_input
        logger.debug(
            "CHATLOG_ID: {} | PARTICIPANT ID: {} | Member check answer: {}".format(
                session["CHATLOG_ID"],
                session["PARTICIPANT_ID"],
                session["MEMBER_CHECK_ANSWER"],
            )
        )

    try:
        response = next_step()
    except TimeoutError as e:
        logger.error(
            "CHATLOG_ID: {} | PARTICIPANT ID: {} | API call failed, retrying".format(
                session["CHATLOG_ID"], session["PARTICIPANT_ID"]
            )
        )
        logger.error(e)
        return {"response": False, "message": END_OF_STUDY_ERROR_MSG}
    except Exception as e:
        logger.error(
            "CHATLOG_ID: {} | PARTICIPANT ID: {} | We faced an uncaught error".format(
                session["CHATLOG_ID"], session["PARTICIPANT_ID"]
            )
        )
        logger.error(e)
        return {"response": False, "message": END_OF_STUDY_ERROR_MSG}

    session["INTERACTION_COUNT"] += 1
    session["QUESTION_ID"] = add_question_to_db(
        response, "INTERVIEWER", session["INTERACTION_COUNT"], "other"
    )
    add_text_to_chatlog(response, "INTERVIEWER")
    # Gets reset to empty string after each main question
    session["RECENT_CHATLOG"].append("{}: {}".format("INTERVIEWER", response))

    return {"response": True, "message": response}


if __name__ == "__main__":
    app.run()
