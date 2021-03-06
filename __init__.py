#coding:utf-8
from flask import Flask, render_template, flash, request, url_for,redirect,session
from wtforms import Form, BooleanField, TextField, PasswordField, validators,TextAreaField
from wtforms.validators import Required
from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
from content_management import Content
from dbconnect import connection
from passlib.hash import sha256_crypt
from functools import wraps
import gc




TOPIC_DICT = Content()


app = Flask(__name__)


@app.route('/<path:text>/')
@app.route('/')
def homepage(text = ''):
    return render_template("support.html")


# @app.route('/<path:text>/')
# @app.route('/')
# def homepage(text = ''):
	# if 'logged_in' in session:
		# try:
			# c, conn = connection()
			# username = session['username']
			# c.execute("select body from blogs where username = %s",username.encode('utf-8'))
			# results = c.fetchall()
			# for result in results:
				# result[0].replace('\r\n', '\n')
			# c.close()
			# conn.close()
			# return render_template("xuexi.html" , results = results)
		# except Exception as e:
			# return (str(e))
	# else:
		# results = []
		# return render_template("support.html" )



# @app.route('/<path:text>/')
# @app.route('/')
# def homepage(text = ''):
	# try:
		# c, conn = connection()
		# c.execute("select body from blogs where username='woyijkl1+'")
		# results = c.fetchall()
		# c.close()
		# conn.close()
		# return (str(results))
	# except Exception as e:
		# return (str(e))



@app.route('/userBlog/')
def userBlog():
	try:
		c, conn = connection()
		c.execute("select username from users ")
		results = c.fetchall()
		c.execute("select username, body,time from blogs order by username ,time desc")
		blog = c.fetchall()
		c.close()
		conn.close()
		return render_template("userBlog.html", results = results , blog = blog)
	except Exception as e:
		return (str(e))



@app.route('/dashboard/')
def dashboard():
    return render_template("dashboard.html", TOPIC_DICT = TOPIC_DICT)



@app.route('/support/')
def support():
    return render_template("support.html")


@app.route('/slashboard/')
def slashboard():
    try:
        return render_template("dashboard.html", TOPIC_DICT = shamwow)
    except Exception as e:
	    return render_template("500.html", error = str(e))
		
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")



def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap


@app.route("/logout/")
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    gc.collect()
    return redirect(url_for('dashboard'))

	
@app.route('/login/', methods=["GET","POST"])
def login_page():
    error = ''
    try:
        c, conn = connection()
        if request.method == "POST":

            data = c.execute("SELECT * FROM users WHERE username = (%s)",
                             thwart(request.form['username']))
            
            data = c.fetchone()[2]

            if sha256_crypt.verify(request.form['password'], data):
                session['logged_in'] = True
                session['username'] = request.form['username']

                flash("You are now logged in")
                return redirect(url_for("myblog"))

            else:
                error = "Invalid credentials, try again."

        gc.collect()

        return render_template("login.html", error=error)

    except Exception as e:
        #flash(e)
        error = "Invalid credentials, try again."
        return render_template("login.html", error = error)  
		




@app.route('/myblog/', methods=["GET","POST"])
def myblog():
	if 'logged_in' in session:
		try:
			c, conn = connection()
			username = session['username']
			c.execute("select body,time from blogs where username = %s order by time desc",username.encode('utf-8'))
			results = c.fetchall()
			for result in results:
				result[0].replace('\r\n', '\n')
			c.close()
			conn.close()
			return render_template("myblog.html" , results = results)
		except Exception as e:
			return (str(e))
	else:
		flash("you need to log in")
		return redirect(url_for('login_page'))  





class blogForm(Form):
	body = TextAreaField("what's on your mind?",validators=[Required()],id='contentcode')




@app.route('/write_blog/', methods=["GET","POST"])
@login_required
def write_blog():
	try:
		form = blogForm(request.form)
		if request.method == "POST" and form.validate():
			if session['logged_in'] == True :
				c, conn = connection()
				data = form.body.data
				username = session['username']
				c.execute("INSERT INTO blogs (username,  body ) VALUES (%s, %s)",
							  (thwart(username.encode('utf-8')), thwart(data.encode('utf-8'))))
				conn.commit()
				c.close()
				conn.close()
				gc.collect()
				flash("new blog article accepted")
			return redirect(url_for('write_blog'))
		else:
			return render_template("write_blog.html", form=form)
	except Exception as e:
		return (str(e))
	

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=20)])
    email = TextField('Email Address', [validators.Length(min=6, max=50)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the Terms of Service and Privacy Notice (updated Jan 22, 2015)', [validators.Required()])
    

@app.route('/register/', methods=["GET","POST"])
def register_page():
    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()

            x = c.execute("SELECT * FROM users WHERE username = (%s)",
                          (thwart(username)))

            if int(x) > 0:
                flash("That username is already taken, please choose another")
                return render_template('register.html', form=form)

            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (%s, %s, %s, %s)",
                          (thwart(username), thwart(password), thwart(email), thwart("/introduction-to-python-programming/")))
                
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username

                return redirect(url_for('dashboard'))

        return render_template("register.html", form=form)

    except Exception as e:
        return(str(e))
		

# @app.route('/register/', methods=["GET","POST"])
# def register_page():
	# return("hello")

if __name__ == "__main__":
    app.run()