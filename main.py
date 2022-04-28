from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from databases.site_news import SiteNews
from databases.users import User
from databases.groups import Group
from databases.posts import Post
from databases.userposts import UserPost
from databases.score import Score
from databases import db_session
from wtforms import PasswordField, SubmitField, StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from flask_login import LoginManager, current_user, login_user, logout_user
import snace
import datetime


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


class CreateUserPostForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    text = TextAreaField("Текст")
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


@app.route('/wall', methods=['GET', 'POST'])
def wall():
    db_sess = db_session.create_session()
    all_groups = db_sess.query(Group).all()
    groups_ids = []
    for i in all_groups:
        subs_ids = i.subscribers_ids.split(",")
        if str(current_user.id) in subs_ids:
            groups_ids.append(i.id)
    posts = db_sess.query(Post).filter(Post.group_id.in_(tuple(groups_ids))).all()
    return render_template('wall.html', posts=posts, title="Главная страница",
                           select_data='По дате: сначала новые.')


@app.route('/wall/sorted', methods=['GET', 'POST'])
def wall_sorted():
    db_sess = db_session.create_session()
    all_groups = db_sess.query(Group)
    groups_ids = []
    for i in all_groups:
        subs_ids = i.subscribers_ids.split(",")
        if str(current_user.id) in subs_ids:
            groups_ids.append(i.id)
    posts = db_sess.query(Post).filter(Post.group_id.in_(tuple(groups_ids))).all()
    return render_template('wall.html', posts=posts, title="Главная страница",
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
    db_sess = db_session.create_session()
    user = db_sess.query(Score).filter_by(user_id=current_user.id).first()
    if not user:
        user = Score(
            user_id=current_user.id,
            game="SnakeGame",
            score="0"
        )
        db_sess.add(user)
        db_sess.commit()
        user = db_sess.query(Score).filter(Score.user_id == current_user.id).first()
        max_score = 0
    else:
        all_scores = user.score.split(',')
        max_score = max([int(i[:i.index("(")]) for i in all_scores[:-1]])
    while True:
        snace_odj = snace.SnakeGame()
        diff = snace_odj.start_screen(snace_odj.RES, snace_odj.RES)
        if diff == 1 or diff == 2 or diff == 3:
            while True:
                score1 = snace_odj.game(diff, max_score)
                break
        break
    user.score += str(score1) + "(" + str(datetime.datetime.now())[:10] + ")" + ","
    db_sess.commit()
    return redirect('/')


@app.route('/user/<int:id>', methods=['GET', 'POST'])
def user_page(id):
    db_sess = db_session.create_session()
    all_posts = db_sess.query(UserPost).filter(UserPost.user_id == id).all()
    return render_template('userpage.html', title=load_user(id).name, userid=id, posts=all_posts)


@app.route('/user/<int:id>/create_post', methods=['GET', 'POST'])
def create_userpost(id):
    form = CreateUserPostForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not form.title:
            return render_template('createuserpost.html', form=form, message="Заголовок обязателен.")
        userpost = UserPost(
            title=form.title.data,
            text=form.text.data,
            user_id=id
        )
        db_sess.add(userpost)
        db_sess.commit()
        return redirect('/user/' + str(id))
    return render_template('createuserpost.html',  form=form)


@app.route('/user/<int:id>/post/<int:postid>', methods=['GET', 'POST'])
def user_post(id, postid):
    db_sess = db_session.create_session()
    post = db_sess.query(UserPost).filter(UserPost.id == postid and UserPost.user_id == id).first()
    return render_template('userpost.html', title=load_user(id).name, userid=id, post=post)


@app.route('/user/<int:id>/records', methods=['GET', 'POST'])
def user_records(id):
    db_sess = db_session.create_session()
    scores = db_sess.query(Score).filter_by(user_id=id).first()
    if scores:
        all_scores = scores.score.split(',')
        snake_highest_score = max([i[:i.index("(")] for i in all_scores[:-1]])
        all_scores = [[i[:i.index("(")], i[i.index("(") + 1:i.index(")")]] for i in all_scores[:-1]
                      if i[:i.index("(")] != '0']
    else:
        all_scores = []
        snake_highest_score = 0
    return render_template('userecords.html', userid=id, scores=all_scores, snake_highest_score=snake_highest_score)


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
    db_sess = db_session.create_session()
    found_groups = db_sess.query(Group).all()
    return render_template('groups.html', title='Группы', found_groups=found_groups)


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
    is_admin = ''
    sids = [[si.id, si.subscribers_ids.split(',')] for si in db_sess.query(Group).all()]
    groups_ids = [sid[0] for sid in sids if str(current_user.id) in sid[1]]
    if group.id in groups_ids:
        is_sub = '1'
    aids = [[ai.id, ai.admins_ids.split(',')] for ai in db_sess.query(Group).all()]
    groups_ids = [aid[0] for aid in aids if str(current_user.id) in aid[1]]
    if group.id in groups_ids:
        is_admin = '1'
    all_posts = db_sess.query(Post).filter(Post.group_id == id)
    return render_template('groupage.html', title=group.name, group=group, allgroups=all_posts, is_sub=is_sub,
                           is_admin=is_admin)


@app.route('/groups/<int:id>/sorted', methods=['GET', 'POST'])
def group_page_sorted(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    all_posts = db_sess.query(Post).filter(Post.group_id == id)
    is_sub = ''
    is_admin = ''
    sids = [[si.id, si.subscribers_ids.split(',')] for si in db_sess.query(Group).all()]
    groups_ids = [sid[0] for sid in sids if str(current_user.id) in sid[1]]
    if group.id in groups_ids:
        is_sub = '1'
    aids = [[ai.id, ai.admins_ids.split(',')] for ai in db_sess.query(Group).all()]
    groups_ids = [aid[0] for aid in aids if str(current_user.id) in aid[1]]
    if group.id in groups_ids:
        is_admin = '1'
    return render_template('groupage.html', title=group.name, group=group, allgroups=all_posts,
                           select_data=request.form['sort_select'], is_sub=is_sub, is_admin=is_admin)


@app.route('/groups/<int:id>/create_post', methods=['GET', 'POST'])
def create_group_post(id):
    db_sess = db_session.create_session()
    group = db_sess.query(Group).filter(Group.id == id).first()
    form = CreatePostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            text=form.text.data,
            anonymously=form.anonymously.data,
            creator=current_user.id,
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
