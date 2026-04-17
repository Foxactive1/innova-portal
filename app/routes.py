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
from .models import Lead, Service, Product
from .database import db
from .utils import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    services = Service.query.all()
    products = Product.query.all()
    return render_template('index.html', services=services, products=products)

@main.route('/add-service', methods=['POST'])
@login_required
def add_service():
    try:
        service = Service(
            titulo=request.form['titulo'],
            descricao=request.form['descricao']
        )
        db.session.add(service)
        db.session.commit()
        flash('Serviço adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao adicionar serviço', 'danger')
    return redirect('/dashboard')

@main.route('/add-product', methods=['POST'])
@login_required
def add_product():
    try:
        product = Product(
            nome=request.form['nome'],
            preco=float(request.form['preco']),
            descricao=request.form['descricao']
        )
        db.session.add(product)
        db.session.commit()
        flash('Produto adicionado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao adicionar produto', 'danger')
    return redirect('/dashboard')

@main.route('/dashboard')
@login_required
def dashboard():
    leads = Lead.query.order_by(Lead.data.desc()).all()
    services = Service.query.all()
    products = Product.query.all()
    return render_template('dashboard.html', leads=leads, services=services, products=products)

@main.route('/contact', methods=['POST'])
def contact():
    try:
        lead = Lead(
            nome=request.form['nome'],
            email=request.form['email'],
            mensagem=request.form['mensagem']
        )
        db.session.add(lead)
        db.session.commit()
        flash('Mensagem enviada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao enviar mensagem', 'danger')
    return redirect('/')

@main.route('/delete-service/<int:id>')
@login_required
def delete_service(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    flash('Serviço removido', 'success')
    return redirect('/dashboard')

@main.route('/delete-product/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto removido', 'success')
    return redirect('/dashboard')