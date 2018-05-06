from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password1@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog = db.Column(db.String(120))
    body = db.Column(db.String(600))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog, body, owner):
        self.blog = blog
        self.body = body
        self.owner = owner


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')

def logged_in_user():
    owner = User.query.filter_by(username=session['user']).first()
    return owner

@app.route("/")
def index():
    users = User.query.all()
    #post_id = request.args.get("id")
    #if post_id:
        #blog_pull = Blog.query.get(post_id)
        #return render_template('main.html', blog_post=blog_pull, post_id=post_id)
    return render_template('index.html', users=users)

@app.route("/blog", methods=['POST', 'GET'])
def list_blogs():
    blogs = Blog.query.all()
    users = User.query.all()
    post_id = request.args.get("id")
    user_id = request.args.get("user")
    if post_id:
        blog_pull = Blog.query.get(post_id)
        return render_template('main.html', blog_post=blog_pull, post_id=post_id)
    if user_id:
        user_pull = Blog.query.filter_by(owner_id=user_id)
        return render_template('main.html', blog_post=user_pull, user_id=user_id)
    return render_template('main.html', blogs=blogs, users=users)

@app.route("/newpost", methods=['POST', 'GET'])
def new_post():

    if request.method == 'POST':
        blog_name = request.form['title']
        blog_content = request.form['post']
        name_error = False
        content_error = False

        if blog_name == "":
            name_error = True

        if blog_content == "":
            content_error = True

        if name_error or content_error == True:
            return render_template("newpost.html", name_error=name_error, content_error=content_error)
        else:
            new_blog = Blog(blog_name, blog_content, logged_in_user())
            db.session.add(new_blog)
            db.session.commit()
            current_id = str(new_blog.id)
            return redirect('./blog?id=' + current_id)

    return render_template('newpost.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        v_password = request.form['v_password']

        username_error = False
        blank_username_error = False
        password_error = False
        blank_password_error = False
        v_password_error = False
        blank_v_password_error = False
        username_exists_error = False

        if len(username) < 3 or len(username) > 20:
            username_error = True

        if username == "":
            blank_username_error = True

        if len(password) < 3 or len(password) > 20:
            password_error = True

        if password == "":
            blank_password_error = True

        if v_password != password:
            v_password_error = True

        if v_password == "":
            blank_v_password_error = True

        if blank_password_error or blank_username_error or blank_v_password_error:
            return render_template("signup.html", blank_password_error=blank_password_error, blank_username_error=blank_username_error, blank_v_password_error=blank_v_password_error)

        users = User.query.filter_by(username=username)
        if users.count() == 1:
            username_exists_error = True

        if username_error or password_error or v_password_error or username_exists_error:
            return render_template("signup.html")
        
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/")

    return render_template("signup.html")

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        blank_password_error = False
        blank_username_error = False
        username_error = False
        password_error = False

        if username == "":
            blank_username_error = True
        
        if password == "":
            blank_password_error = True

        if blank_username_error or blank_password_error == True:
            return render_template('login.html', blank_username_error=blank_username_error, blank_password_error=blank_password_error)

        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if user.password == password:
                session['user'] = user.username
                return redirect("/")
            else:
                password_error = True
        else:
            username_error = True
        
        if username_error or password_error == True:
            return render_template('login.html', username_error=username_error, password_error=password_error)



#@app.route("/index", methods=['GET'])
#def index():
    #users = User.query.all()
    #post_id = request.args.get("id")
    #if post_id:
        #blog_pull = Blog.query.get(post_id)
        #return render_template('main.html', blog_post=blog_pull, post_id=post_id)
    #return render_template('index.html', users=users)


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    del session['user']
    return redirect("/blog")

app.secret_key = 'wow secret'

if __name__ == '__main__':
    app.run()