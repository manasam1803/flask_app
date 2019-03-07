
from flask import Flask,render_template,redirect,url_for,logging,session,request,flash
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,IntegerField,validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.debug=True

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Manasa18*'
app.config['MYSQL_DB'] = 'mydatabase'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)




@app.route('/')
def index():

    return render_template('home.html')




class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            flash('User name already exists', 'success')
            return redirect(url_for('register'))
        else:
            cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('afterlogin'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')





def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap




# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))




# afterlogin
"""
@app.route('/afterlogin')
def afterlogin():
    return render_template('afterlogin.html')
"""

class EnterOwnDataForm(Form):
     commodity = IntegerField('commodity')


@app.route('/afterlogin',methods = ['GET','POST'])
def afterlogin():
  petrol1 = 0
  grocery1 = 0
  entertainment1 = 0
  if session['username']:
    form = EnterOwnDataForm(request.form)
    selection = ['petrol','grocery','entertainment']
    if request.method == 'POST' and form.validate():
         if form.commodity.data < 0:
             flash('Not valid!!!')
             return redirect(url_for('afterlogin'))
         var = selected()
         if var == 'petrol':
            petrol = form.commodity.data
            grocery = 0
            entertainment = 0
         if var == 'grocery':
            grocery = form.commodity.data
            petrol = 0
            entertainment =0
         if var == 'entertainment':
            entertainment = form.commodity.data
            petrol = 0
            grocery = 0
         temp = session['username']

         cur = mysql.connection.cursor()
         result = cur.execute('SELECT count(id) FROM eachuser2')
         x = cur.execute('SELECT id FROM users WHERE username = %s ',[temp])

         cur.fetchone()
         print('dff',cur.fetchone())
         cur.execute('SELECT id FROM users WHERE username = %s ',[temp])
         trial = cur.fetchone()
         trial1 = trial.get('id')
         print(trial1)
         if result > 0:
             cur.execute('SELECT SUM(petrol) FROM eachuser2 WHERE id = %s',[x])
             trial = cur.fetchone()
             petrol1 = int(trial.get('SUM(petrol)'))
             cur.execute('SELECT SUM(grocery) FROM eachuser2 WHERE id = %s',[x])
             trial = cur.fetchone()
             grocery1 = int(trial.get('SUM(grocery)'))
             cur.execute('SELECT SUM(entertainment) FROM eachuser2 WHERE id = %s',[x])
             trial = cur.fetchone()
             entertainment1 = int(trial.get('SUM(entertainment)'))
         print(result)
         selected()
         cur.execute("INSERT INTO eachuser2(id,petrol,grocery,entertainment) VALUES (%s, %s, %s, %s)",(x,petrol-1,grocery-1,entertainment-1))


         mysql.connection.commit()
         cur.close()
         return render_template('personal.html',form = form,selection = selection,petrol1 = petrol1,grocery1 = grocery1,entertainment1 = entertainment1)

    return render_template('personal.html',form = form,selection = selection)
  else:
     return 'go back and login'

def selected():
    dropdown = request.form.get('selection')
    print(dropdown)
    return dropdown

class FriendForm(Form):
     friend = StringField('friendname')


"""
@app.route('/addfriends',methods = ['POST','GET'])
def addfriends():
    form = FriendForm(request.form)
    if request.method == 'POST':
        friend = form.friendname.data
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM users WHERE username != %s',session['username'])
        print(cur.fetchall())
        return render_template('addfriends.html',form = form)
    return render_template('addfriends.html',form = form)
"""
if __name__=="__main__":
    app.secret_key='secret123'
    app.run()
