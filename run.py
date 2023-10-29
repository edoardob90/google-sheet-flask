import sys

from web_app import create_app

if __name__ == "__main__":
    app = create_app()
    print(app.url_map, file=sys.stderr)
    app.run(debug=True)
else:
    gunicorn_app = create_app()
