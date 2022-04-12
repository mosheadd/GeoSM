from flask import Flask, render_template, redirect, abort
from flask_wtf import FlaskForm
from databases.site_news import SiteNews
from databases.users import User
from databases import db_session
from wtforms import PasswordField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired

from flask_login import LoginManager, current_user, login_user, logout_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_kkkey'

login_manager = LoginManager()
login_manager.init_app(app)


class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class SignInForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    submit = SubmitField('Применить')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    db_sess = db_session.create_session()
    all_news = db_sess.query(SiteNews)
    return render_template('mainpage.html', sitenews=all_news, title="Главная страница")


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/")
    return render_template('signing_in.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first() and db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('signing_up.html', form=form, message="Такой пользователь уже есть.")
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('signing_up.html', form=form, message="Пользователь с таким именем уже есть.")
        if db_sess.query(User).filter(User.login == form.login.data).first():
            return render_template('signing_up.html', form=form, message="Пользователь с таким логином уже есть.")
        user = User(
            name=form.name.data,
            login=form.login.data,
            password=form.password.data
        )
        user.set_password(user.password)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('signing_up.html', form=form)


@app.route('/user/<int:id>', methods=['GET', 'POST'])
def user_page(id):
    return render_template('userpage.html', title=load_user(id).name)


@app.route('/user')
def current_user_page():
    return redirect('/user/' + str(current_user.id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/add_news')
def add_news():
    form = NewsForm()
    return render_template('addnews.html', title='Добавить новость', form=form)


def main():
    db_session.global_init("databases/sitenews.db")
    app.run()


if __name__ == "__main__":
    main()
