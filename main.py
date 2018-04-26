from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password1@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    blog = db.Column(db.String(120))
    body = db.Column(db.String(600))

    def __init__(self, blog, body):
        self.blog = blog
        self.body = body

@app.route("/")
def wrong():
    return redirect("/blog")

@app.route("/blog", methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    post_id = request.args.get("id")
    if post_id:
        blog_pull = Blog.query.get(post_id)
        return render_template('main.html', blog_post=blog_pull, post_id=post_id)
    return render_template('main.html', blogs=blogs)

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
            new_blog = Blog(blog_name, blog_content)
            db.session.add(new_blog)
            db.session.commit()
            current_id = str(new_blog.id)
            return redirect('./blog?id=' + current_id)

    return render_template('newpost.html')

if __name__ == '__main__':
    app.run()