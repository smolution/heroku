# -*- coding: utf-8 -*-
"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask_login import login_required, login_user, logout_user, current_user
from flask import render_template, flash, redirect, sessions, url_for, request, g
from AtelierApp import app, db, lm
from AtelierApp.forms import LoginForm, ContactForm
from AtelierApp.decorators import required_roles
from emails import send_contactForm



@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    """Renders the home page."""
    user = g.user
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash(u'Děkujeme za zprávu, brzy se Vám ozveme.')
        send_contactForm(form)
        return redirect(url_for('index'))
    return render_template(
        'contact.html',
        title='Kontakt',
        year=datetime.now().year,
        form=form
    )

@app.route('/about')
@required_roles('Admin')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash(u'Uživatel %s neexistuje.' % form.email.data)
            return redirect(url_for('login', **request.args))
        if not user.verify_password(form.password.data):
            flash(u'Nesprávné heslo')
            return redirect(url_for('login', **request.args))
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html', title='Sign In', form=form, year=datetime.now().year)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
