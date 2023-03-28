from flask import Flask, render_template, redirect, request, session, abort, \
    jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, \
    current_user
from flask_restful import Api

from data import db_session, news_api
from data.news import News
from data.users import User
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from news_resource import NewsResource, NewsListResource
from users_resource import UserResource, UserListResource

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

api.add_resource(NewsListResource, '/api/v2/news')
api.add_resource(NewsResource, '/api/v2/news/<int:news_id>')

api.add_resource(UserListResource, '/api/v2/users')
api.add_resource(UserResource, '/api/v2/users/<int:user_id>')


@app.route('/')
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1',
                       max_age=60 * 60 * 24 * 365 * 2)
    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    del session['visits_count']
    session.permanent = True
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_api.blueprint)
    app.run(host='0.0.0.0', port=5000)


def db_work():
    db_session.global_init("db/blogs.db")

    db = db_session.create_session()
    db.add(News(title="n-ая новость", content="Приватка",
                user_id=4, is_private=True))
    db.add(News(title="(n+1)-ая новость", content="Публичка",
                user_id=4, is_private=False))
    db.commit()
    # select * from users
    # for user in db.query(User).all():
    #     print(user)

    # select * from users WHERE
    # for user in db.query(User)\
    #         .filter(User.id > 1, User.email.notilike("%1%")):
    #     print(user)

    # for user in db.query(User)\
    #         .filter((User.id > 1) | (User.email.notilike("%42%"))):
    #     print(user)

    # user = db.query(User).filter(User.id == 1).first()
    # print(user)
    # user.name = "Измененное имя пользователя"
    # user.created_date = datetime.now()
    # db.commit()

    #
    # user = db_sess.query(User).filter(User.id == 1).first()

    # news = News(title="Первая новость", content="Привет блог!",
    #             user_id=1, is_private=False)
    # db_sess.add(news)
    #
    # second_news = News(title="Вторая новость", content="Уже вторая запись!",
    #             user=user, is_private=False)
    # db_sess.add(second_news)
    #
    # private_news = News(title="Личная запись", content="Эта запись личная",
    #             is_private=True)
    # user.news.append(private_news)
    #
    # db_sess.commit()
    #
    # for news in user.news:
    #     print(news)


from flask import make_response


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    main()
