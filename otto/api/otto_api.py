import datetime
import os
from functools import wraps

import jwt
from flask import Flask, jsonify, request
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.config import RunnableConfig

from otto.api.flask_db import db
from otto.api.models.entities import Entities
from otto.otto_logger.logger_config import logger
from otto.ryu.intent_engine.intent_processor_pool import IntentProcessorPool
from otto.ryu.network_state_db.processed_intents_db_operator import ProcessedIntentsDbOperator


class OttoApi:
    _app: Flask
    _intent_processor_pool: IntentProcessorPool

    def __init__(self):

        db_user = os.getenv("OTTO_DB_USER")
        db_pwd = os.getenv("OTTO_DB_PWD")
        db_host = os.getenv("OTTO_DB_HOST")
        db_port = os.getenv("OTTO_DB_PORT")
        db_name = os.getenv("OTTO_DB_NAME")

        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = os.urandom(16)
        self.app.config[
            'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SQLALCHEMY_POOL_RECYCLE'] = 280
        self.app.config['SQLALCHEMY_POOL_PRE_PING'] = True
        self.app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20

        db.init_app(self.app)

        self._processed_intents_db_conn = ProcessedIntentsDbOperator()

        self.intent_processor_pool = IntentProcessorPool()

        self._create_routes()

    def _create_routes(self):
        """ Creates route to be used by Flask app"""

        def validate_token(func):
            """
            Function to valid JWT token passed in each request after /login
            """

            @wraps(func)
            def wrapped(*args, **kwargs):
                token = request.headers['Authorization']

                if not token:
                    return jsonify({'message': 'Access token not found'}), 403

                try:
                    token = token.split(" ")[1]
                    token_data = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])

                except Exception as e:
                    logger.warn(e)
                    return jsonify({'message': 'Invalid token'}), 403

                return func(*args, **kwargs)

            return wrapped

        @self.app.route('/login', methods=['POST'])
        def app_login():
            """
            Login function to authenticate a user/network application before using northbound interface.
            The /login route is used by the streamlit dashboard to authenticate a user, as well as being used to
            authenticate users/ network apps which consume the different REST API endpoints. Returns a JWT token
            to be used in subsequent API calls.

            Fields to be added in POST request body:
                username: Username for the user or the registered application name
                password: Password for the associated user/application.

            """

            login_request = request.get_json()

            if not login_request:
                return jsonify(
                    {
                        'message': 'Empty request body. Please provide the following fields: method (either application or user), username, password'
                    }), 403

            if 'username' not in login_request or 'password' not in login_request:
                return jsonify(
                    {'message': 'Username AND Password are required for network application authentication'}), 403

            found_user = db.session.query(Entities).filter_by(username=login_request['username']).first()

            if found_user and found_user.check_password(login_request['password']):
                token = jwt.encode({
                    'app': login_request['username'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600)
                }, self.app.config['SECRET_KEY'], algorithm='HS256')

                return jsonify({'token': token})

            else:
                return jsonify(
                    {
                        'message': f"Incorrect username/password for {login_request['method']} {login_request['username']}"}), 403

        @self.app.route("/declare-intent", methods=['POST'])
        @validate_token
        def process_intent():

            token = request.headers['Authorization']
            token = token.split(" ")[1]
            token_data = jwt.decode(token, self.app.config['SECRET_KEY'], algorithms=['HS256'])

            intent_request = request.get_json()

            if not intent_request or 'intent' not in intent_request:
                return jsonify({'message': 'No intent found'}), 403

            if 'model' not in intent_request or not intent_request['model']:
                designated_processor = self.intent_processor_pool.get_intent_processor('gpt-4o')
            else:
                designated_processor = self.intent_processor_pool.get_intent_processor(intent_request['model'])

            designated_processor.context, intent = token_data["app"], intent_request['intent']

            messages, config = [HumanMessage(content=intent)], RunnableConfig(recursion_limit=300)

            result = designated_processor.graph.invoke({"messages": messages}, config)

            resp = ""

            for m in result['messages']:
                if isinstance(m, AIMessage):
                    if isinstance(m.content, str):
                        resp += m.content + " "
                    else:
                        resp += m.content[0].get("text", "") + " "

            self.intent_processor_pool.return_intent_processor(designated_processor)

            if 'stream_type' in intent_request and 'stream_type' == 'AgentMessages':
                return jsonify({'message': resp, 'operations': result['operations']})
            else:
                return jsonify({'message': resp, 'operations': result['operations']})

        @self.app.route('/latest-activity', methods=['GET'])
        @validate_token
        def get_latest_activity():
            response = self._processed_intents_db_conn.get_latest_activity()

            return jsonify({'message': response})

        @self.app.route('/weekly-activity', methods=['GET'])
        @validate_token
        def get_weekly_activity():
            response = self._processed_intents_db_conn.get_weekly_activity()

            return jsonify({'message': response})

        @self.app.route('/top-activity', methods=['GET'])
        @validate_token
        def get_top_activity():
            response = self._processed_intents_db_conn.get_top_activity()

            return jsonify({'message': response})

        @self.app.route('/model-usage', methods=['GET'])
        @validate_token
        def get_model_activity():
            response = self._processed_intents_db_conn.get_model_usage()

            return jsonify({'message': response})

    def run(self):
        self.app.run()
