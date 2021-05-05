from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_from_directory
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import os



app = Flask(__name__)
app.debug = True
app.secret_key=os.environ['KEY']
app.config['MYSQL_HOST'] = os.environ['HOST']
app.config['MYSQL_USER'] = os.environ['USER']
app.config['MYSQL_PASSWORD'] = os.environ['PASS']
app.config['MYSQL_DB'] = os.environ['DB']
app.config['MYSQL_CURSORCLASS'] = os.environ['CURSORCLASS']
mysql=MySQL(app)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def index():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")



class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=4,max=25)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#USER REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        

        #Create cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO admin (username, password) VALUES (%s ,%s )",(username,password))

        #CommitToDB
        mysql.connection.commit()

        #Close Connection
        cur.close()

        flash("You are now registered and can log in", 'success')

        return redirect (url_for('about'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        #GET FORM FIELDS
        username = request.form['username']
        passwordCandidate = request.form['password']


        #CREATE CURSOR
        cur = mysql.connection.cursor()

        #GET USER BY USERNAME
        result = cur.execute("SELECT * FROM admin WHERE username = %s",[username])

        if result > 0:
            #GET STORED HASH
            data = cur.fetchone()
            password = data['password']

            #COMPARE PASSWORDS
            if sha256_crypt.verify(passwordCandidate,password):
                #PASSED
                session['logged_in'] = True
                session['username'] = username


                flash('You are now logged in', 'success')
                return redirect (url_for ('about'))
            else:
                error = 'Invalid password or username'
                return render_template('login.html', error=error)
            #CLOSE CONNECTION
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    return render_template('login.html')

#CHECK IF USER LOGGED IN
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized. Please log in", 'danger')
            return redirect (url_for('login'))
    return wrap

def is_logged_out(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            flash("Unauthorized. Please log out", 'danger')
            return redirect (url_for('about'))
        else:
            return f(*args, **kwargs)
            flash("Unauthorized. Please log in", 'danger')
            return redirect (url_for('login'))
    return wrap


#LOG OUT
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect (url_for('login'))

@app.route('/oxygen')
@is_logged_out
def oxygen():
    cur4=mysql.connection.cursor()
    cur4.execute("SELECT * FROM oxygen")
    row=cur4.fetchall()
    cur4.close()
    return render_template('oxygen.html', oxygen=row)


@app.route('/beds')
@is_logged_out
def beds():
    cur3=mysql.connection.cursor()
    cur3.execute("SELECT * FROM beds")
    row=cur3.fetchall()
    cur3.close()
    return render_template('beds.html', beds=row)



@app.route('/oxygenadmin')
@is_logged_in
def oxygenadmin():
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM oxygen")
    row=cur2.fetchall()
    cur2.close()
    return render_template('oxygenadmin.html', oxygen=row)
    



@app.route('/insert', methods=['POST'])
@is_logged_in
def insert():
    if request.method == 'POST':
        flash("Data inserted successfully", 'success')
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        place = request.form['place']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO oxygen(name, contact, email, place) VALUES (%s, %s, %s, %s)",(name,contact,email,place))
        mysql.connection.commit()
        
        return redirect (url_for('oxygenadmin'))
    return render_template ('oxygenadmin.html')


@app.route('/update', methods=['POST','GET'])
@is_logged_in
def update():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        place = request.form['place']

        cur=mysql.connection.cursor()
        cur.execute("""
        UPDATE oxygen
        SET name = %s, contact= %s, email=%s, place=%s
        WHERE id=%s
        """,(name, contact, email, place, id_data))
        flash ("Data updated successfully!!",'success')
        mysql.connection.commit()
        return redirect(url_for('oxygenadmin'))

@app.route('/delete/<string:id_data>',methods=['POST','GET'])
@is_logged_in
def delete(id_data):
    
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM oxygen WHERE id=%s",(id_data))
    mysql.connection.commit()
    flash("Data deleted successfully", 'danger')
    return redirect (url_for('oxygenadmin'))


@app.route('/bedsadmin')
@is_logged_in
def bedsadmin():
    cur2=mysql.connection.cursor()
    cur2.execute("SELECT * FROM beds")
    row=cur2.fetchall()
    cur2.close()
    return render_template('bedsadmin.html', beds=row)

@app.route('/insertwo', methods=['POST'])
@is_logged_in
def insertwo():
    if request.method == 'POST':
        flash("Data inserted successfully", 'success')
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        beds = request.form['beds']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO beds(name, contact, email, beds) VALUES (%s, %s, %s, %s)",(name,contact,email,beds))
        mysql.connection.commit()
        
        return redirect (url_for('bedsadmin'))
    return render_template ('bedsadmin.html')

@app.route('/updatwo', methods=['POST','GET'])
@is_logged_in
def updatwo():
    if request.method == 'POST':
        id_data = request.form['id']
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        beds = request.form['beds']

        cur=mysql.connection.cursor()
        cur.execute("""
        UPDATE beds
        SET name = %s, contact= %s, email=%s,beds=%s
        WHERE id=%s
        """,(name, contact, email, beds, id_data))
        flash ("Data updated successfully!!",'success')
        mysql.connection.commit()
        return redirect(url_for('bedsadmin'))

@app.route('/deletwo/<string:id_data>',methods=['POST','GET'])
@is_logged_in
def deletwo(id_data):
    
    cur=mysql.connection.cursor()
    cur.execute("DELETE FROM beds WHERE id=%s",(id_data))
    mysql.connection.commit()
    flash("Data deleted successfully", 'danger')
    return redirect (url_for('bedsadmin'))

    


if __name__ == "__main__":
    app.run()
