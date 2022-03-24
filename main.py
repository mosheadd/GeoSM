from flask import Flask

from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET KEY'] = 'mosheadd176440'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    app.run()


if __name__ == "__main__":
    main()
