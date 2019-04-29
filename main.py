from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import jinja2
import os
import cgi
from hashutils import make_pw_hash, check_pw_hash

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
    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    def __init__(self,username,password):
        self.username = username
        self.pw_hash = make_pw_hash(password)
    def __repr__(self):
        return self.username

@app.route('/',methods=['POST','GET'])
def index():
    owners = User.query.all()
    return render_template('index.html',title="owners", owners=owners )
    


@app.route("/blog", methods=["POST","GET"])
def blog():
    blog_id = request.args.get('id')
    owner_id = request.args.get('owner')
    
    if (owner_id):
        blogs = Blog.query.filter_by(owner_id=owner_id).all()
        owner = User.query.filter_by(id=owner_id).first()
        return render_template("userposts.html",blogs=blogs, owner=owner)
    if (blog_id):
        blog = Blog.query.get(blog_id)
        return render_template('individualblog.html', title="Blog Entry", blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html',title="blogs", blogs=blogs)


        

@app.route("/newpost", methods=["POST","GET"])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':

        title = request.form['title']
        content = request.form['content']
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

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        error_msg = ''
    
        if not user:
            error_msg = "User does not exist"
            
        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        else:
            error_msg = "Incorrect username or password"
            template = jinja_env.get_template('login.html')
            return template.render(error_msg=error_msg)
        

            

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        error_msg = ''
        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        
        if len(username) <3 or len(password) <3 or len(username) <3:
            error_msg='Username and password must be greater than 3 characters'
            

        if verify != password:
            error_msg='Passwords dont match' 
            

        if existing_user:
            flash('Username already exists','error')
            error_msg='User already exists'
            
        if not error_msg:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            template = jinja_env.get_template('signup.html')
            return template.render(error_msg=error_msg)



            
        
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')        


@app.before_request
def require_login():
    allowed_routes = ['login', 'blog','index','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


if __name__=='__main__':
    app.run()
        