from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from passlib.hash import bcrypt_sha256

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '1234'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idUser = db.Column(db.Integer)
    titleTask = db.Column(db.String(300), nullable=False)
    textTask = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return "<Task %r>" % self.id

    def check_title(self, title):
        return self.title == title

    def get_id(self):
        return str(self.id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = bcrypt_sha256.hash(password)

    def check_password(self, password):
        return bcrypt_sha256.verify(password, self.password_hash)

    def get_id(self):
        return str(self.id)

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_anonymous():
        return False


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/base", methods=['POST', 'GET'])
def insert():
    if request.method == 'POST':
        task = Task(titleTask=request.form['titleTask'], textTask=request.form['textTask'], idUser=current_user.id)
        try:
            db.session.add(task)
            db.session.commit()
            print("add")
            return redirect('/base')
        except:
            return "При добавление возникла ошибка "
    else:
        task = Task(titleTask="", textTask="")
        tasks = Task.query.all()
        return render_template("view.html", tasks=tasks, task=task, idus=current_user.id)


@app.route("/base/delete/<int:id>")
def delete(id):
    try:
        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()
        return redirect('/base')
    except:
        return "Ошибка удаления"


@app.route("/base/<int:id>", methods=['POST', 'GET'])
def update(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        taskUpd = Task.query.get_or_404(id)
        taskUpd.titleTask = request.form['titleTask']
        taskUpd.textTask = request.form['textTask']
        try:
            db.session.commit()
            return redirect('/base')
        except:
            return "При добавление возникла ошибка "
    else:
        tasks = Task.query.all()
        return render_template("view.html", task=task, tasks=tasks, idus=current_user.id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']

        existing_user = User.query.filter_by(username=userName).first()
        if existing_user:
            flash('Данный пользователь уже существует', 'error')
            return redirect('/register')

        user = User(username=userName, password=password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/login')
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']

        user = User.query.filter_by(username=userName).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect('/base')
        else:
            flash('Неправильный email или пароль', 'error')
            return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")


@app.route('/clear_database')
def clear_database():
    db.drop_all()
    db.create_all()
    return 'База данных очищена и пересоздана'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=1)
