import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")




@app.route("/", methods=["GET", "POST"])
def main():
   if request.method == "GET":
      return render_template('main.html')

   if request.method == "POST":

      #Register
      register = request.form.get("register-button")
      if  register != None:
         #Check if username valid
         if not request.form.get('register-username'):
            flash("Please enter a username" , "alert")
            return redirect("/")

         #Check if password valid
         elif not request.form.get('register-password'):
            flash("Please enter a password" , "alert")
            return redirect("/")

         #Check if password confirmation valid
         elif not request.form.get('password-confirmation'):
            flash("Please confirm your password" , "alert")
            return redirect("/")

         #Get username and password into variable
         username = request.form.get('register-username')
         password = request.form.get('register-password')
         confirmation = request.form.get('password-confirmation')

         if confirmation != password:
            flash("Passwords didn't match please try again" , "alert")
            return redirect("/")


         #Check if username and password is long enough
         if len(username) < 3 or len(username) > 12 or len(password) < 3:
            flash("Your username or password is not long enough" , "alert")
            return redirect("/")

         #Hash the password
         hash = generate_password_hash(password)


         #Check if username already existed
         existed_user = db.execute("SELECT username FROM users WHERE username = ?", (username))
         if len(existed_user) == 1:
            flash("This username already exists" , "alert")
            return redirect("/")

         #Check if the user who is registering is the first user
         rows = db.execute("SELECT COUNT(*) FROM users")
         if rows == 0:
            id = 1
            db.execute("INSERT INTO users (id, username, hash) VALUES (?, ?, ?)", id,username,hash)
         #If not
         else:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username,hash)


         #Get user_id
         user_id = db.execute("SELECT id FROM users WHERE username = ?", (username))

         #Save the session by using user_id
         session["user_id"] = user_id[0]["id"]
         flash("successfully registered, please click on Start Now to achieve your goals." , "success")
         return redirect("/")

      #Login
      login = request.form.get("login-button")
      if  login != None:

         session.clear()

         if not request.form.get("login-username"):
            flash("Please enter your username" , "alert")
            return redirect("/")

         elif not request.form.get("login-password"):
            flash("Please enter your password" , "alert")
            return redirect("/")

         rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("login-username"))

         if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("login-password")):
            flash("Invalid username or password" , "alert")
            return redirect("/")

         session["user_id"] = rows[0]["id"]

         flash("Successfully logged in, please click on Start Now to achieve your goals." , "success")
         return redirect("/")



      #Log out
      logout = request.form.get("logout")
      if  logout != None:
         session.clear()
         flash("Logged out!" , "success")
         return redirect("/")


      #Start Now
      start_now = request.form.get("start-now")
      if  start_now != None:
         if 'user_id' in session:
            user_id = session["user_id"]
            goal = db.execute("SELECT goal FROM users where id = ?",user_id)
            tasks = db.execute("SELECT task_name,task_points,id FROM tasks WHERE user_id = ?", user_id)
            return render_template("profile.html", tasks = tasks, goal = goal[0]['goal'])
         else:
            flash("Please first login" ,"success")
            return redirect("/")

      return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
def profile():
   if request.method == "POST":

      setgoal = request.form.get("setgoal-button")
      if  setgoal != None:
         goal = request.form.get('goal')
         user_id = session["user_id"]
         db.execute("UPDATE users SET goal = ? WHERE id = ?", goal, user_id)
         score = db.execute("SELECT score FROM users WHERE id = ?" ,user_id)
         tasks = db.execute("SELECT task_name,task_points,id FROM tasks WHERE user_id = ?", user_id)
         return render_template('profile.html', tasks = tasks, goal = goal, score=score[0]['score'])

      addtask = request.form.get("addtask-button")
      if addtask != None:
         #Note for myself add something to check inputs
         user_id = session["user_id"]
         task_name = request.form.get('task-name')
         task_points = request.form.get('task-points')
         db.execute("INSERT INTO tasks (user_id, task_name, task_points) VALUES (?,?,?)" , user_id, task_name, task_points)
         goal = db.execute("SELECT goal FROM users where id = ?",user_id)
         tasks = db.execute("SELECT task_name,task_points,id FROM tasks WHERE user_id = ?", user_id)
         score = db.execute("SELECT score FROM users WHERE id = ?" ,user_id)
         print(score)
         return render_template("profile.html" , tasks = tasks, goal = goal[0]['goal'], score=score[0]['score'])


      delete = request.form.get("delete")
      if delete != None:
         user_id = session["user_id"]
         db.execute("DELETE FROM tasks WHERE id = ?", delete)
         goal = db.execute("SELECT goal FROM users where id = ?",user_id)
         tasks = db.execute("SELECT task_name,task_points,id FROM tasks WHERE user_id = ?", user_id)
         score = db.execute("SELECT score FROM users WHERE id = ?" ,user_id)
         return render_template("profile.html", tasks = tasks, goal = goal[0]['goal'], score=score[0]['score'])

      done = request.form.get("done")
      if done != None:
         user_id = session["user_id"]
         score_old = db.execute("SELECT score FROM users WHERE id = ?" ,user_id)

         plus = db.execute("SELECT task_points FROM tasks WHERE id = ?", done)

         score = score_old[0]['score'] + plus[0]['task_points']

         db.execute("UPDATE users SET score = ? WHERE id = ?", score,user_id)
         goal = db.execute("SELECT goal FROM users where id = ?",user_id)
         tasks = db.execute("SELECT task_name,task_points,id FROM tasks WHERE user_id = ?", user_id)
         return render_template("profile.html", tasks = tasks, goal = goal[0]['goal'], score=score)

   #After Refresh
   user_id = session["user_id"]
   goal = db.execute("SELECT goal FROM users where id = ?",user_id)
   tasks = db.execute("SELECT task_name,task_points,id FROM tasks WHERE user_id = ?", user_id)
   score = db.execute("SELECT score FROM users WHERE id = ?" ,user_id)
   return render_template("profile.html", tasks = tasks, goal = goal[0]['goal'], score=score)















