#---------------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      DIONE CASTRO ALVES
#
# Created:     16/04/2026
# Copyright:   (c) DIONE CASTRO ALVES 2026
# Licence:     <your licence>
#---------------------------------------------------------------------------------------

from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .database import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.username
            flash('Login realizado com sucesso!', 'success')
            return redirect('/dashboard')
        else:
            flash('Usuário ou senha inválidos', 'danger')

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Nome de usuário já existe', 'danger')
            return redirect('/register')

        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado! Faça login.', 'success')
        return redirect('/login')

    return render_template('register.html')

@auth.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logout efetuado', 'info')
    return redirect('/')