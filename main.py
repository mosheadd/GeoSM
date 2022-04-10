from flask import Flask, make_response, render_template

from flask_login import LoginManager, current_user


app = Flask(__name__)
app.config['SECRET KEY'] = 'mosheadd176440'

login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main_page():
    return render_template('main_page_not_signed_in.html')


def main():
    app.run()


if __name__ == "__main__":
    main()
