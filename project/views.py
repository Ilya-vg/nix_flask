from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    print(current_user)
    return 'Add movie'


@views.route('/delete-movie', methods=['POST'])
def delete_note():
    return 'Delete movie'