import os
from datetime import datetime

from flask import \
    Flask, \
    request, \
    render_template, \
    session, \
    redirect, \
    url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from forms import NameForm

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Configura chave secreta
app.config['SECRET_KEY'] = 'Hard to guees string'
# Configura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('FLASKY_MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('FLASKY_MAIL_PASSWORD')
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@flasky.com>'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __repr__(self):
        return '<User %r>' % self.username


@app.route('/', methods=['GET', 'POST'])
def index():
    user_agent = request.headers.get('User-Agent')
    print(user_agent)
    name = None
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['know'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New user', 'mail/new_user', user=user)
        else:
            session['know'] = True
        session['name'] = form.name.data
        form.name.data = ''
        redirect(url_for('index'))
    return render_template(
        'index.html',
        current_time=datetime.utcnow(),
        form=form,
        name=session.get('name'),
        know=session.get('know', False)
    )


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


def send_email(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
