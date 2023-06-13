from flask import Blueprint, flash, url_for, redirect
# from webapp.chat import c

bp = Blueprint("home", __name__)

@bp.route('/', methods=['GET'])
def index():
    print("get home")
    flash("home", "info")
    return redirect(url_for('chat.index'))

