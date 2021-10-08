import logging
import os
from datetime import datetime as dt

from dotenv import load_dotenv

from flask import Flask, request

from web_app import spreadsheet, edit
from web_app.flask_logs import LogSetup

load_dotenv()

def create_app(test_config=None):
    """Flask app configuration"""
    app = Flask(__name__, instance_relative_config=True)

    # config app
    app.config.from_mapping(
        SECRET_KEY = os.environ.get("SECRET_KEY"),
        ENV = os.environ.get("FLASK_ENV"),
        SPREADSHEET_OBJ = spreadsheet.Spreadsheet(app),
        # logging
        LOG_DIR = os.environ.get("LOG_DIR", "./"),
        LOG_TYPE = os.environ.get("LOG_TYPE", "stream"),
        LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO"),
        APP_LOG_NAME = os.environ.get("APP_LOG_NAME", "app.log"),
        WWW_LOG_NAME = os.environ.get("WWW_LOG_NAME", "www.log"),
        LOG_MAX_BYTES = os.environ.get("LOG_MAX_BYTES", 100_000_000), # 100 MB
        LOG_COPIES = os.environ.get("LOG_COPIES", 5)
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup logging
    logs = LogSetup(app)

    @app.after_request
    def after_request(response):
        """Logging after every request"""
        logger = logging.getLogger("app.access")
        logger.info(
            "%s [%s] %s %s %s %s %s %s %s",
            request.remote_addr,
            dt.utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
            request.method,
            request.path,
            request.scheme,
            response.status,
            response.content_length,
            request.referrer,
            request.user_agent
        )

        return response

    @app.route('/')
    def hello():
        return "Hello, World!"

    # register blueprints
    app.register_blueprint(edit.bp)

    return app
