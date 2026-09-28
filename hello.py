import re
from datetime import datetime

from flask import (Flask, render_template, session, redirect, url_for, flash,
                   request)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    email = EmailField('What is your UofT Email address?',
                       validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed your name!')
        old_email = session.get('email')
        if old_email is not None and old_email != form.email.data:
            flash('Looks like you have changed your email!')
        session['name'] = form.name.data
        session['email'] = form.email.data
        if 'utoronto' in form.email.data:
            return redirect(url_for('chat_page'))
        return redirect(url_for('index'))
    return render_template('index.html', form=form,
                           name=session.get('name'),
                           email=session.get('email'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


def is_logged_in():
    return bool(session.get('name')) and 'utoronto' in session.get('email', '')


@app.route('/chat', methods=['GET'])
def chat_page():
    if not is_logged_in():
        return redirect(url_for('index'))
    return render_template('chat.html', name=session['name'])


@app.route('/chat', methods=['POST'])
def chat():
    if not is_logged_in():
        return {'reply': 'Please sign in from the Home page first.'}, 401
    data = request.get_json(silent=True) or {}
    message = str(data.get('message', '')).strip()
    if not message:
        return {'reply': 'Please type a message.'}, 400

    lowered = message.lower()
    told_name = re.search(r"\bmy name is\s+(.+)", message, re.IGNORECASE)
    if told_name:
        # remembered in the session, which lives in the signed cookie
        session['bot_name'] = told_name.group(1).strip(' .!?')
        reply = 'Nice to meet you, {}!'.format(session['bot_name'])
    elif re.search(r"what(?:'s| is) my name|who am i", lowered):
        if 'bot_name' in session:
            reply = 'Your name is {}.'.format(session['bot_name'])
        else:
            reply = "I don't know your name yet. Tell me by saying 'My name is ...'."
    elif 'hello' in lowered:
        reply = 'Hello!'
    else:
        reply = "I don't understand."
    return {'reply': reply}


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))
