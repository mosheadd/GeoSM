from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from databases.site_news import SiteNews
from databases.users import User
from databases.groups import Group
from databases.posts import Post
from databases import db_session
from wtforms import PasswordField, SubmitField, StringField, TextAreaField, BooleanField
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
    content = TextAreaField("Содержание", validators=[DataRequired()])
    quickdescription = TextAreaField("Краткое содержание")
    submit = SubmitField('Применить')


class AddCreateGroupForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    about = TextAreaField("Описание")
    everyone_can_post = BooleanField()
    submit = SubmitField('Применить')


class CreatePostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField("Текст")
    anonymously = BooleanField()
    submit = SubmitField('Опубликовать')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def main_page():
    db_sess = db_session.create_session()
    all_news = db_sess.query(SiteNews)
    return render_template('mainpage.hstml', sitenews=all_news, title="Главная страница")


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


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route('/add_news', methods=['GET', 'POST'])
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if len(form.quickdescription.data) >= 80:
            return render_template('addnews.html', title='Добавить новость', form=form,
                                   message="Краткое содержание должно иметь не более 80 символов(включая пробелы)")
        news = SiteNews(
            title=form.title.data,
            content=form.content.data,
            quickdescription=form.quickdescription.data
        )
        db_sess.add(news)
        db_sess.commit()
        return redirect('/')
    return render_template('addnews.html', title='Добавить новость', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
def news_page(id):
    db_sess = db_session.create_session()
    news = db_sess.query(SiteNews).filter(SiteNews.id == id).first()
    return render_template('newspage.html', title=news.title, sitenews=news)


@app.route('/delete_news/<int:id>', methods=['GET', 'POST'])
def delete_news(id):
    db_sess = db_session.create_session()
    delete_this = db_session.sa.delete(SiteNews).where(SiteNews.id == id)
    db_sess.execute(delete_this)
    db_sess.commit()
    return redirect('/')


@app.route('/groups')
def groups():
    return render_template('groups.html', title='Группы')


@app.route('/groups/managing')
def groups_managing():
    db_sess = db_session.create_session()
    all_groups = db_sess.query(Group).filter(Group.admins_ids == current_user.id)
    return render_template('groupsmanaging.html', title='Ваши группы', groups=all_groups)


@app.route('/groups/group_creating', methods=['GET', 'POST'])
def create_group():
    form = AddCreateGroupForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Group).filter(Group.name == form.title.data).first():
            return render_template('addgroup.html', form=form, message="Группа с таким название уже существует.")
        group = Group(
            name=form.title.data,
            about=form.about.data,
            admins_ids=str(current_user.id)
        )
        if form.everyone_can_post.data:
            group.everyone_can_post = 1
        else:
            group.everyone_can_post = 0
        db_sess.add(group)
        db_sess.commit()
        return redirect('/groups/managing')
    return render_template('addgroup.html', form=form)


@app.route('/groups/<int:id>', methods=['GET', 'POST'])
def group_page(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    all_posts = db_sess.query(Post).filter(Post.group_id == id)
    return render_template('groupage.html', title=group.name, group=group, allgroups=all_posts)


@app.route('/groups/<int:id>/create_post', methods=['GET', 'POST'])
def create_group_post(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    creator = db_sess.query(User).filter(User.id == current_user.id).first()
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            text=form.text.data,
            anonymously=form.anonymously.data,
            creator=creator.id,
            group_id=id
        )
        db_sess.add(post)
        db_sess.commit()
        return redirect('/groups/' + str(id))
    return render_template('createpost.html', group=group, form=form)


def main():
    db_session.global_init("databases/sitenews.db")
    app.run()


if __name__ == "__main__":
    main()
