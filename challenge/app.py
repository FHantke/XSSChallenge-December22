from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_assets import Environment, Bundle
from flask_login import LoginManager
import flask_login
from sanitizer import sanitize_html
from uuid import uuid4
import secrets
import os
import re

app = Flask(__name__)
app.secret_key = os.urandom(12).hex()

postgres_user = os.environ.get("POSTGRES_USER", default="user")
postgres_db = os.environ.get("POSTGRES_DB", default="blog")
postgres_password = os.environ.get("POSTGRES_PASSWORD", default="secret")
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{postgres_user}:{postgres_password}@db/{postgres_db}"

app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = True

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.session_protection = "strong"

assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('assets/style.scss', filters='libsass', output='css/style.css')
assets.register('scss_all', scss)

class User(db.Model, flask_login.UserMixin):
    __tablename__ = "user"
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    tags = db.Column(db.String)
    comments = db.relationship("Comment", back_populates="user")

class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    user_id = db.Column(db.String, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="comments")


def init_defaults():
    if User.query.first() is None:
        from data import users
        for user_dict in users:
            user = User(
                id=user_dict["id"],
                username=user_dict["name"],
                content=user_dict["content"],
                tags=user_dict["tags"]
            )
            db.session.add(user)
    db.session.commit()

with app.app_context():
    db.create_all()
    init_defaults()

def get_user(user_id=None, name=None):
    user = db.session.query(User).filter(
        (User.id==user_id) | (User.username == name)
    ).first()
    return user

@app.before_request 
def generate_nonce():
    g.nonce = secrets.token_hex()

@app.after_request
def add_security_headers(resp):
    if 'nonce' not in g:
        g.nonce = secrets.token_hex()
    resp.headers['Content-Security-Policy'] = f"default-src 'self'; script-src 'self' 'nonce-{g.nonce}' 'strict-dynamic'; img-src * data:;"
    return resp
    
@app.context_processor
def add_nonce():
    return dict(nonce=g.nonce)

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash(e.description, 'danger')
    return redirect(request.url)    

@login_manager.user_loader
def user_loader(user_id):
    return get_user(user_id)

@login_manager.unauthorized_handler
def unauthorized_handler():    
    flash('Login first to see this side.', 'danger')
    return redirect(url_for('login'))
    
@app.route("/")
@app.route("/challenge")
def index_view():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    name = request.form['name']    
    if get_user(name):
        flash('The username is already in use.', 'danger')
        return redirect(url_for('login'))

    user = User(
        id=str(uuid4()),
        username=name,
        content= "Edit me!",
        tags = ""
    )
    db.session.add(user)
    db.session.commit()
    flask_login.login_user(user)
    flash('You successfully logged in.', 'success')
    return redirect(url_for('edit_view'))

@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('You successfully logged out.', 'secondary')
    return redirect(url_for('index_view'))

@app.route("/blog/<user_id>")
def user_view(user_id):
    user = get_user(user_id)    
    if not user:
        flash('This blog does not exist.', 'danger')
        return redirect(url_for('index_view'))
    return render_template("blog.html", blog_user=user)

@app.route("/comment/<user_id>", methods=['POST'])
def send_comment(user_id):
    user = get_user(user_id)

    if not user.is_authenticated:
        return redirect("/")

    name = request.form.get('name', None)
    text = request.form.get('text', None)

    if not name or not text:
        flash('You need a name and text for your comment.', 'danger')
        return redirect(f"/user/{user_id}")

    comment = Comment(text=text, name=name)
    db.session.add(comment)
    user.comments.append(comment)
    db.session.commit()

    flash('You successfully commented this blog.', 'success')
    return redirect(f"/blog/{user_id}")

@app.route("/edit", methods=['GET', 'POST'])
@flask_login.login_required
def edit_view():
    if request.method == 'GET':
        return render_template("editor.html")
        
    content = request.form.get('content', None)
    tags = request.form.get('tags', None)

    dif = os.environ.get("DIFFICULTY", default="medium")
    print(f"DIF is {dif}")
    if dif == "hard":
        print(f"{tags}")
        tags = re.sub(r'[^a-zA-Z0-9,]', '', tags)
        print(f"{tags}")
    
    if not content or not tags:
        flash('You need content and tags for your post.', 'danger')
        return redirect(f"/edit")

    content = sanitize_html(content)
    flask_login.current_user.content = content
    flask_login.current_user.tags = tags
    db.session.commit()


    return redirect(f"/blog/{flask_login.current_user.id}")    

if __name__ == '__main__':
    db.create_all()
    init_defaults()
    app.run()
