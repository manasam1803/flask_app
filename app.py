
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
  print(session['username'])
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
         result = cur.execute('SELECT count(id) FROM expenses')

         print(result)
         cur.execute('SELECT id FROM users WHERE username = %s ',[temp])

         x_temp = cur.fetchone()
         x = x_temp.get('id')
         #print('dff',cur.fetchone())
         cur.execute('SELECT id FROM users WHERE username = %s ',[temp])
         trial = cur.fetchone()
         trial1 = trial.get('id')
         cur.execute("INSERT INTO expenses(id,petrol,grocery,entertainment) VALUES (%s, %s, %s, %s)",(x,petrol,grocery,entertainment))
         #print(trial1)
         selected()
         #cur.execute("INSERT INTO eachuser2(id,petrol,grocery,entertainment) VALUES (%s, %s, %s, %s)",(x,petrol-1,grocery-1,entertainment-1))

         if result > 0:
             cur.execute('SELECT SUM(petrol) FROM expenses WHERE id = %s  and month(addtime) = month(now())',[x])
             trial = cur.fetchone()
             petrol1 = int(trial.get('SUM(petrol)'))
             cur.execute('SELECT SUM(grocery) FROM expenses WHERE id = %s  and month(addtime) = month(now())',[x])
             trial = cur.fetchone()
             grocery1 = int(trial.get('SUM(grocery)'))
             cur.execute('SELECT SUM(entertainment) FROM expenses WHERE id = %s and month(addtime) = month(now())',[x])
             trial = cur.fetchone()
             entertainment1 = int(trial.get('SUM(entertainment)'))
                 #print(result)

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
     friend = StringField('friend')


@app.route('/addfriends',methods = ['POST','GET'])
def addfriends():
    list_friends = []
    if session['username'] != None:
       print(session['username'])
       form = FriendForm(request.form)
       if request.method == 'POST':
            friend = form.friend.data
            cur = mysql.connection.cursor()
            print(friend)
            cur.execute('SELECT id FROM users WHERE username = %s',[friend])
            temp_dict = cur.fetchone()
            print(temp_dict)
            temp = temp_dict.get('id')

            flag = session['username']
            cur.execute('SELECT id FROM users WHERE username = %s',[flag])
            temp1_dict = cur.fetchone()
            temp1 = temp1_dict.get('id')
            print(temp,temp1)
            cur.execute('SELECT friend_id FROM friends2 WHERE id = %s',[temp1])
            dict_friends = cur.fetchall()
            list_friends = []

            for i in range(len(dict_friends)):
                 cur.execute('select username from users where id = %s',[dict_friends[i].get('friend_id')])
                 var = cur.fetchone()
                 list_friends.append(var.get('username'))
            list_friends = Remove(list_friends)
            print(list_friends)
            #friend_list = dict_friends.keys()
            #print(friend_list)
            check = 0
            for j in range(len(list_friends)):
                if temp == list_friends[j]:
                   check = 1
                   break;
                else:
                   continue

            if check == 0:
                 cur.execute('INSERT INTO friends2(id,friend_id) VALUES (%s ,%s)',(temp1,temp))
                 cur.execute('INSERT INTO friends2(id,friend_id) VALUES (%s ,%s)',(temp,temp1))

            #print(result)

            mysql.connection.commit()
            cur.close()
            return render_template('addfriends.html',form = form,friend_list = list_friends)
       return render_template('addfriends.html',form = form,friend_list = list_friends)
    else :
        redirect(url_for('login'))

def Remove(duplicate):
    final_list = []
    for num in duplicate:
        if num not in final_list:
            final_list.append(num)
    return final_list

class MoneyForm(Form):
    money = IntegerField('money')
    friend = StringField('friend')

@app.route('/addmoney',methods = ['GET','POST'])
def addmoney():
      form = MoneyForm(request.form)
      username_list = []
      friend_list = []
      debtfriend_list = []
      debtfriend_money = []
      debtfriend_list1 = []
      debtfriend_money1 = []
      if request.method == 'POST':
          money = form.money.data
          friend = form.friend.data
          cur = mysql.connection.cursor()
          session_username = session['username']
          cur.execute('select id from users where username = %s',[session_username])
          id_dict = cur.fetchone()
          session_id = id_dict.get('id')
          cur.execute('select friend_id from friends2 where id = %s',[session_id])

          dict_friends = cur.fetchall()
          print(dict_friends)
          for i in range(len(dict_friends)):
                friend_list.append(dict_friends[i].get('friend_id'))
                cur.execute('select username from users where id = %s',[friend_list[i]])
                temp_dict = cur.fetchone()

                temp = temp_dict.get('username')

                username_list.append(temp)
          flag = 0
          for i in range(len(username_list)):
                if friend == username_list[i]:
                    flag = 1
                    break;
          if flag == 0:
              return render_template('addmoney.html',form=form)
          for j in range(len(username_list)):
              if friend == username_list[j]:
                  cur.execute('select id from users where username = %s',[friend])
                  temp_dict = cur.fetchone()
                  print(temp_dict)
                  temp = temp_dict.get('id')
                  print(temp)
                  cur.execute('insert into mymoney(id,friend_id,money) values (%s,%s,%s)',(session_id,temp,money))
                  break;


          mysql.connection.commit()
          cur.close()
          cur = mysql.connection.cursor()
          cur.execute('select * from mymoney where id = %s',[session_id])
          y1 = cur.fetchall()
          print(y1)
          g1 = []
          z1 = []
          for i in range(len(y1)):
              cur.execute('select username from users where id = %s',[y1[i].get('friend_id')])
              var1 = cur.fetchone()
              z1.append(var1.get('username'))
              g1.append(y1[i].get('money'))
          print(z1)
          print(g1)



          cur.execute('select * from mymoney where friend_id = %s',[session_id])
          y = cur.fetchall()
          print(y)
          g = []
          z = []
          for i in range(len(y)):
              cur.execute('select username from users where id = %s',[y[i].get('id')])
              var = cur.fetchone()
              z.append(var.get('username'))
              g.append(y[i].get('money'))

          print(z)
          print(g)
          mysql.connection.commit()
          cur.close()
          return render_template('addmoney.html',friend = friend,money = money,form = form,zipped_data = zip(z1,g1),zipped_data1 = zip(z,g))
      return render_template('addmoney.html',form = form)


if __name__=="__main__":
    app.secret_key='secret123'
    app.run()
