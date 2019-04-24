from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import jinja2
import os
import cgi

template_dir = os.path.join(os.path.dirname(__file__),
    'templates')
jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abc123'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __init__(self, title, content, user):
        self.title = title
        self.content = content
        self.user = user

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.route("/blog", methods=["POST","GET"])
def blog():
    blog_id = request.args.get('id')
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('individualblog.html', title="Blog Entry", blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="blogs", blogs=blogs, )

        

@app.route("/newpost", methods=["POST","GET"])
def newpost():
    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
        owner = request.form['owner']
        error_msg=""

        if len(title) <= 0 or len(content) <=0:
            error_msg = "cannot leave either field blank"

        if error_msg:
            template = jinja_env.get_template('newpost.html')
            return template.render(error_msg=error_msg)
        else:
            new_blog = Blog(title,content,owner)
            db.session.add(new_blog)
            db.session.commit()
            
            ind_blog_url = "/blog?id=" + str(new_blog.id)
            return redirect(ind_blog_url)
            
    


    template = jinja_env.get_template('newpost.html')
    return template.render()
        



if __name__=='__main__':
    app.run()
        