from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db, bcrypt


# Define a blueprint for routes
main_blueprint = Blueprint('main', __name__)

@main_blueprint.route('/')
@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'name' in session:
            flash('You are already logged in!', 'info')
            return redirect(url_for('main.home'))
        return render_template('login.html')
    
    return redirect(url_for('main.home'))

@main_blueprint.route('/home')
def home():
    # Render the generate page
    return render_template('home.html')


@main_blueprint.route('/generate')
def generate():
    # Render the generate page
    return render_template('generate.html')
