from flask import Flask, make_response

from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET KEY'] = 'mosheadd176440'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main_page():
    return make_response('Здесь ничего не происходит.')





def main():
    app.run()


if __name__ == "__main__":
    main()
