import logging
import os
import pathlib as pl
from datetime import datetime as dt

from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap4 as Bootstrap

from web_app import user
from web_app.flask_logs import LogSetup
from web_app.models import Users
from web_app.spreadsheet import Spreadsheet

load_dotenv()

APP_DIR = pl.Path(__file__).parent


def create_app(test_config=None):
    """Flask app configuration"""
    # Setup app
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    # Config app
    app.config.from_mapping(
        APP_DIR=APP_DIR,
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        ENV=os.environ.get("FLASK_ENV"),
        USERS=Users(),
        SPREADSHEET_OBJ=Spreadsheet(APP_DIR.parent / "service_account.json"),
        # logging
        LOG_DIR=os.environ.get("LOG_DIR", "./"),
        LOG_TYPE=os.environ.get("LOG_TYPE", "stream"),
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        APP_LOG_NAME=os.environ.get("APP_LOG_NAME", "app.log"),
        WWW_LOG_NAME=os.environ.get("WWW_LOG_NAME", "www.log"),
        LOG_MAX_BYTES=os.environ.get("LOG_MAX_BYTES", 100_000_000),  # 100 MB
        LOG_COPIES=os.environ.get("LOG_COPIES", 5),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Setup logging
    LogSetup(app)

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
            request.user_agent,
        )

        return response

    # Routes
    @app.route("/")
    def index():
        return render_template("index.html")

    # Register blueprints
    app.register_blueprint(user.bp)

    return app
