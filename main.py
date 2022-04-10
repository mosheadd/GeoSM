from flask import Flask, make_response, render_template
from databases.site_news import SiteNews
from databases.users import User
from databases import db_session

from flask_login import LoginManager, current_user


app = Flask(__name__)
app.config['SECRET KEY'] = 'mosheadd176440'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    db_sess = db_session.create_session()
    all_news = db_sess.query(SiteNews)
    return render_template('main_page_not_signed_in.html', sitenews=all_news)


def main():
    db_session.global_init("databases/sitenews.db")
    app.run()


if __name__ == "__main__":
    main()
