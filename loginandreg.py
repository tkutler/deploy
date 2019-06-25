from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
from flask_bcrypt import Bcrypt 
app = Flask(__name__)
bcrypt= Bcrypt(app)
import re
app.secret_key = "I am a secret key" 
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
db ="admin"


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods= ["POST"])
def register():
    mysql = connectToMySQL(db)
        
    if len(request.form['first']) < 1:
    	flash("Please enter a valid first name")
    if len(request.form['last']) <1:
        flash("Please enter valid last name") 
    if len(request.form["password"]) < 1:
        flash("password lenth must be more than 0 ")
    if len(request.form["passwordconfirm"]) < 1:
        flash("password lenth must be more than 0 ")
    if request.form['password'] != request.form['passwordconfirm']:
        flash ("passsword does not match")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address!")
    if '_flashes' in session.keys():
        return redirect("/")
    if not '_flashes' in session.keys(): 
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        
        query = "INSERT INTO users (first, last, email, password,user_level) VALUES (%(first)s, %(last)s, %(email)s, %(pw)s, %(user_level)s); "
        data = {
            "first": request.form["first"],
            "last": request.form["last"],
            "email": request.form["email"],
            "pw": pw_hash,
            "user_level": 9
        }
        userid = mysql.query_db(query,data)
        session['userid'] = userid
        session['user_level'] = 9
        mysql = connectToMySQL(db)
        query = "SELECT first FROM users WHERE idusers =" + str(userid)+";"
        username = mysql.query_db(query,data)
        session["username"] = username[0]['first']
        return redirect ("/success")
@app.route("/login", methods = ["POST"]) 
def login():
    mysql = connectToMySQL(db)
    query = "SELECT * FROM users WHERE email = %(email)s;"
    data = {
        "email" : request.form['userlogin']
    }
    users = mysql.query_db(query, data)
    
    
    if users: 
        if bcrypt.check_password_hash(users[0]['password'], request.form['passwordlogin']):
            session['userid'] = users[0]['idusers']
            session['username'] = users[0]['first']
            print("password found")
            mysql = connectToMySQL(db)
            query = "SELECT * from users WHERE user_level = 0;" 
            print ("runnion")
            
            admins = mysql.query_db(query)
            if admins: 
                print ('you are admin')
                session['user_level'] = 0
                return redirect ("/admin")
                

            else:
                session['user_level'] = 9
                return redirect("/success")
        else: 
            flash("not successful")
            print("password not found")
            return redirect ("/")
    else: 
        flash("not successful") 
        print("email not found")  
        return redirect ("/") 

    
@app.route("/success")
def success():
    return render_template("user.html") 
@app.route('/logout')
def logout():
    session.clear()
    print('you are logged out')
    return redirect ('/') 
@app.route("/admin")
def show ():
    print ("in admin route")
    if session["user_level"] == 9:
        return render_template("notallowed.html")
    else:
        mysql = connectToMySQL(db)
        query= "select * from users" 
        allusers = mysql.query_db(query) 
        
        return render_template ("admin.html", allusers = allusers) 
@app.route ("/removeuser/<id>")
def removeuser(id): 
    mysql = connectToMySQL(db)
    query ="DELETE FROM users WHERE idusers ="+ id +";"
    mysql.query_db(query) 
    return redirect ("/admin")

@app.route("/makeadmin/<id>")
def makeadmin(id):
    mysql = connectToMySQL(db)
    query = "UPDATE users SET user_level='0' WHERE idusers ="+ id + ";" 
    mysql.query_db(query)
    return redirect ("/admin")
@app.route("/removeadmin/<id>")
def removeadmin(id):
    mysql = connectToMySQL(db)
    query = "UPDATE users SET user_level='9' WHERE idusers ="+ id + ";" 
    mysql.query_db(query)
    return redirect ("/admin")




    

















if __name__ == "__main__":
    app.run(debug=True)