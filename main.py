from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from databases.site_news import SiteNews
from databases.users import User
from databases.groups import Group
from databases.posts import Post
from databases import db_session
from wtforms import PasswordField, SubmitField, StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from flask_login import LoginManager, current_user, login_user, logout_user
import snace.py


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


@app.route('/', methods=['GET', 'POST'])
def main_page():
    db_sess = db_session.create_session()
    all_news = db_sess.query(SiteNews)
    return render_template('mainpage.html', sitenews=all_news, title="Главная страница",
                           select_data='По дате: сначала новые.')


@app.route('/sorted', methods=['GET', 'POST'])
def main_page_sorted():
    db_sess = db_session.create_session()
    all_news = db_sess.query(SiteNews)
    return render_template('mainpage.html', sitenews=all_news, title="Главная страница",
                           select_data=request.form['sort_select'])


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
        user.is_site_admin = 0
        user.set_password(user.password)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('signing_up.html', form=form)


@app.route('/game', methods=['GET', 'POST'])
def start_game():
    while True:
        diff = snace.start_screen(snace.RES, snace.RES)
        if diff == 1 or diff == 2 or diff == 3:
            while True:
                snace.game(diff)
    return redirect('/')


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


@app.route('/groups', methods=['GET', 'POST'])
def groups():
    return render_template('groups.html', title='Группы', found_groups='NO_REQUEST')


@app.route('/groups/searching', methods=['GET', 'POST'])
def groups_find():
    db_sess = db_session.create_session()
    requested_title = request.form["search_data"]
    search = "%{}%".format(requested_title)
    found_groups = db_sess.query(Group).filter(Group.name.like(search)).all()
    return render_template('groups.html', title='Группы', found_groups=found_groups)


@app.route('/groups/managing')
def groups_managing():
    db_sess = db_session.create_session()
    aids = [[ai.id, ai.admins_ids.split(',')] for ai in db_sess.query(Group).all()]
    groups_ids = [aid[0] for aid in aids if str(current_user.id) in aid[1]]
    all_groups = db_sess.query(Group).filter(Group.id.in_(tuple(groups_ids))).all()
    return render_template('groupsmanaging.html', title='Ваши группы', groups=all_groups)


@app.route('/groups/group_creating', methods=['GET', 'POST'])
def create_group():
    form = AddCreateGroupForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Group).filter(Group.name == form.title.data).first():
            return render_template('addgroup.html', form=form, message="Группа с таким названием уже существует.")
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
    is_sub = ''
    sids = [[si.id, si.subscribers_ids.split(',')] for si in db_sess.query(Group).all()]
    groups_ids = [sid[0] for sid in sids if str(current_user.id) in sid[1]]
    if group.id in groups_ids:
        is_sub = '1'
    all_posts = db_sess.query(Post).filter(Post.group_id == id)
    return render_template('groupage.html', title=group.name, group=group, allgroups=all_posts, is_sub=is_sub)


@app.route('/groups/<int:id>/sorted', methods=['GET', 'POST'])
def group_page_sorted(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    all_posts = db_sess.query(Post).filter(Post.group_id == id)
    print(request.form['sort_select'])
    return render_template('groupage.html', title=group.name, group=group, allgroups=all_posts,
                           select_data=request.form['sort_select'])


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


@app.route('/groups/<int:id>/subscribe')
def group_subscribing(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    group.subscribers_ids += ',' + str(current_user.id)
    db_sess.commit()
    return redirect('/groups/' + str(group.id))


@app.route('/groups/<int:id>/unsubscribe')
def group_unsubscribing(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    sids = [si.subscribers_ids.split(',') for si in db_sess.query(Group).all()]
    new_sids = sids[group.id - 1]
    new_sids.remove(str(current_user.id))
    new_sids_str = ""
    for i in new_sids:
        new_sids_str += i
    group.subscribers_ids = new_sids_str
    db_sess.commit()
    return redirect('/groups/' + str(group.id))


def main():
    db_session.global_init("databases/sitenews.db")
    app.run()


if __name__ == "__main__":
    main()
