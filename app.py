import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from datetime import datetime as date
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
import bcrypt
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
def home():
    return render_template('login.html')

@app.route("/new-user")
def newuser():
    return render_template('register.html')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        check = request.form.get("password2")
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username")
            })

        existing_email = mongo.db.users.find_one({
            "email": request.form.get("email")
            })

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        if existing_email:
            flash("Email already in use")
            return redirect(url_for("register"))   
                
        if password != check:
            flash("passwords are not equal")
            return redirect(url_for("register")) 

        mongo.db.users.insert_one({
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": generate_password_hash(request.form.get("password"))
        })
        session["user"] = request.form.get("username")
        flash("Registration Successful!")
    return render_template("login.html")

@app.route("/login",methods=["GET", "POST"])
def login():
     if request.method == "POST":

        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username")})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username")
                return redirect(url_for(
                        "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

     return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    goal = list(mongo.db.Goals.find({"user": session["user"]}))
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile.html", username=username ,files=file,goals=goal)

@app.route("/profile-completed/<username>", methods=["GET", "POST"])
def profilecompleted(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    goal = list(mongo.db.Goals.find({"user": session["user"],"Completed":"Complete"}))
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile-completed.html", username=username ,files=file,goals=goal)

@app.route("/profile-inprogress/<username>", methods=["GET", "POST"])
def profileinprogress(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    goal = list(mongo.db.Goals.find({"user": session["user"],"Completed":"Incomplete"}))
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    return render_template("profile-inprogress.html", username=username ,files=file,goals=goal)

@app.route('/Upload/<username>', methods=['POST'])
def upload(username):
    profile_image = request.files['profile_image']
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    test = mongo.db.files.find_one({"id": session["user"]})
    if not test:
        mongo.save_file(profile_image.filename,profile_image)
        mongo.db.files.insert({'id': session["user"],'profile_image_name':profile_image.filename})
        return redirect(url_for("profile", username=username))
    else:
        mongo.db.files.remove({"id": session["user"]})
        mongo.save_file(profile_image.filename,profile_image)
        mongo.db.files.insert({'id': session["user"],'profile_image_name':profile_image.filename})
        return redirect(url_for("profile", username=username))

@app.route('/Upload-completed/<username>', methods=['POST'])
def uploadcompleted(username):
    profile_image = request.files['profile_image']
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    test = mongo.db.files.find_one({"id": session["user"]})
    if not test:
        mongo.save_file(profile_image.filename,profile_image)
        mongo.db.files.insert({'id': session["user"],'profile_image_name':profile_image.filename})
        return redirect(url_for('profilecompleted', username=username,files=file))
    else:
        mongo.db.files.remove({"id": session["user"]})
        mongo.save_file(profile_image.filename,profile_image)
        mongo.db.files.insert({'id': session["user"],'profile_image_name':profile_image.filename})
        return redirect(url_for('profilecompleted', username=username,files=file))


@app.route('/Upload-inprogress/<username>', methods=['POST'])
def uploadinprogress(username):
    profile_image = request.files['profile_image']
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    test = mongo.db.files.find_one({"id": session["user"]})
    if not test:
        mongo.save_file(profile_image.filename,profile_image)
        mongo.db.files.insert({'id': session["user"],'profile_image_name':profile_image.filename})
        return redirect(url_for('profileinprogress', username=username,files=file))
    else:
        mongo.db.files.remove({"id": session["user"]})
        mongo.save_file(profile_image.filename,profile_image)
        mongo.db.files.insert({'id': session["user"],'profile_image_name':profile_image.filename})
        return redirect(url_for('profileinprogress', username=username,files=file))


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route("/logout")
def logout():
    session.pop("user")
    return redirect(url_for("login"))

@app.route("/MyWorkouts/<username>", methods=["GET", "POST"])
def workouts(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    workout = list(mongo.db.Workouts.find({"user": session["user"]}))
    return render_template("workouts.html", username=username,files=file, workouts=workout)


@app.route("/Add-Workouts/<username>", methods=["GET", "POST"])
def addworkout(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    if request.method == 'POST':
        mongo.db.Workouts.insert_one(
            {
                'user': session["user"],
                "Date": date.today().strftime("%d/%m/%Y"),
                'Title': request.form['Title'],
                'Routine': request.form['Routine'],
                'Difficulty': request.form['Difficulty'],
                'Shared':False,
            })
    return redirect(url_for('workouts', username=username))



@app.route('/delete-workout/<username>_<workout_id>')
def deleteworkout(workout_id, username):
    mongo.db.Workouts.remove({'_id': ObjectId(workout_id)})
    return redirect(url_for('workouts', username=username))


@app.route('/edit-workout/<username>_<workout_id>')
def editworkout(workout_id, username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    edit = mongo.db.Workouts.find_one({'_id': ObjectId(workout_id)})
    workout = list(mongo.db.Workouts.find({"user": session["user"]}))
    return render_template('update-workout.html', username=username, edit=edit, workouts=workout,files=file)



@app.route('/updated-workout/<username>_<workout_id>', methods=['POST'])
def updateworkout(workout_id, username):
    edit = mongo.db.Workouts.find_one({'_id': ObjectId(workout_id)})
    updates = {
             'user': session["user"],
             "Date": edit['Date'],
             'Title': request.form['Title'],
             'Routine': request.form['Routine'],
             'Difficulty': request.form['Difficulty']
        }
    mongo.db.Workouts.update({"_id": ObjectId(workout_id)}, updates)
    return redirect(url_for('workouts', username=username))

@app.route("/SharedWorkouts/<username>", methods=["GET", "POST"])
def sharedworkouts(username):
    file = list(mongo.db.files.find())
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    sharedworkout = list(mongo.db.Sharedworkouts.find())
    return render_template("sharedworkouts.html", username=username, files=file, workouts=sharedworkout)

@app.route("/Saved-SharedWorkouts/<username>", methods=["GET", "POST"])
def savedsharedworkouts(username):
    file = list(mongo.db.files.find())
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    sharedworkout = list(mongo.db.Sharedworkouts.find())
    return render_template("savedsharedworkouts.html", username=username, files=file, workouts=sharedworkout)

@app.route("/Add-SharedWorkouts/<username>", methods=["GET", "POST"])
def addsharedworkout(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    if request.method == 'POST':
        saved=[]
        mongo.db.Sharedworkouts.insert_one(
            {
                'user': session["user"],
                "Date": date.today().strftime("%d/%m/%Y"),
                'Title': request.form['Title'],
                'Routine': request.form['Routine'],
                'Difficulty': request.form['Difficulty'],
                'Savedby': saved
            })
    return redirect(url_for('sharedworkouts', username=username))

@app.route('/delete-Sharedworkout/<username>_<workout_id>')
def deleteSharedworkout(workout_id, username):
    mongo.db.Sharedworkouts.remove({'_id': ObjectId(workout_id)})
    return redirect(url_for('sharedworkouts', username=username))

@app.route('/edit-Sharedworkout/<username>_<workout_id>')
def editSharedworkout(workout_id, username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    edit = mongo.db.Sharedworkouts.find_one({'_id': ObjectId(workout_id)})
    workout = list(mongo.db.Sharedworkouts.find({"user": session["user"]}))
    return render_template('update-Sharedworkout.html', username=username, edit=edit, workouts=workout,files=file)

@app.route('/update-Sharedworkout/<username>_<workout_id>')
def updateSharedworkout(workout_id, username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    edit = mongo.db.Sharedworkouts.find_one({'_id': ObjectId(workout_id)})
    workout = list(mongo.db.Sharedworkouts.find({"user": session["user"]}))
    return render_template('update-Sharedworkout.html', username=username, edit=edit, workouts=workout,files=file)

@app.route('/save-Sharedworkout/<username>_<workout_id>')
def saveSharedworkout(workout_id, username):
    edit = mongo.db.Sharedworkouts.find_one({'_id': ObjectId(workout_id)})
    saved= edit['Savedby']
    if session["user"] in  saved:
        return redirect(url_for('sharedworkouts', username=username))
    else:
         saved.append(session["user"])
         updates = {
                'user': edit['user'],
                "Date": edit['Date'],
                'Title': edit['Title'],
                'Routine': edit['Routine'],
                'Difficulty': edit['Difficulty'],
                'Savedby': saved
            }
         mongo.db.Sharedworkouts.update({"_id": ObjectId(workout_id)}, updates)
    return redirect(url_for('sharedworkouts', username=username))





@app.route('/Shareexistingworkout/<username>_<workout_id>', methods=['GET','POST'])
def shareexisitingworkout(workout_id, username):
    share = mongo.db.Workouts.find_one({'_id': ObjectId(workout_id)})
    saved=[]
    mongo.db.Workouts.update_one({'_id': ObjectId(workout_id)}, {"$set": {"Shared": True}}, upsert=False)
    if request.method == 'POST':
        mongo.db.Sharedworkouts.insert_one(
            {
                'user': session["user"],
                "Date": share['Date'],
                'Title': share['Title'],
                'Routine': share['Routine'],
                'Difficulty': share['Difficulty'],
                'Savedby': saved
            })
    print(share)
    return redirect(url_for('workouts', username=username))


@app.route("/Add-Goal/<username>", methods=["GET", "POST"])
def addgoal(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    if request.method == 'POST':
        mongo.db.Goals.insert_one(
            {
                'user': session["user"],
                "Date": date.today().strftime("%d/%m/%Y"),
                'Title': request.form['Title'],
                'Details': request.form['Details'],
                'Completed': "Incomplete"
            })
    return redirect(url_for('profile', username=username,files=file))



@app.route('/edit-goal/<username>_<goal_id>')
def editgoal(goal_id, username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
    goal = list(mongo.db.Goals.find({"user": session["user"]}))
    return render_template('update-profile.html', username=username, edit=edit, goals=goal,files=file)

@app.route('/updated-goal/<username>_<goal_id>', methods=['POST'])
def updategoal(goal_id, username):
    edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
    if not request.form['Details']:
        details = edit["Details"]
    else:
        details = request.form['Details']
    updates = {
             'user': session["user"],
             "Date": edit['Date'],
             'Title': request.form['Title'],
             'Details': details,
             'Completed': request.form['Completed']
        }
    mongo.db.Goals.update({"_id": ObjectId(goal_id)}, updates)
    return redirect(url_for('profile', username=username,files=file))


@app.route('/edit-goalcompleted/<username>_<goal_id>')
def editgoalcompleted(goal_id, username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
    goal = list(mongo.db.Goals.find({"user": session["user"],"Completed":"Complete"}))
    return render_template('update-profile-completed.html', username=username, edit=edit, goals=goal,files=file)
    
@app.route('/delete-goal/<username>_<goal_id>')
def deletegoal(goal_id, username):
    mongo.db.Goals.remove({'_id': ObjectId(goal_id)})
    return redirect(url_for('profile', username=username,files=file))


@app.route('/updated-completedgoal/<username>_<goal_id>', methods=['POST'])
def updategoalcompleted(goal_id, username):
    edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
    if not request.form['Details']:
        details = edit["Details"]
    else:
        details = request.form['Details']
    updates = {
             'user': session["user"],
             "Date": edit['Date'],
             'Title': request.form['Title'],
             'Details': details,
             'Completed': request.form['Completed']
        }
    mongo.db.Goals.update({"_id": ObjectId(goal_id)}, updates)
    return redirect(url_for('profilecompleted', username=username,files=file))


@app.route('/delete-goalcompleted/<username>_<goal_id>')
def deletegoalcompleted(goal_id, username):
    mongo.db.Goals.remove({'_id': ObjectId(goal_id)})
    return redirect(url_for('profilecompleted', username=username,files=file))



@app.route('/edit-goalinprogress/<username>_<goal_id>')
def editgoalinprogress(goal_id, username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
    goal = list(mongo.db.Goals.find({"user": session["user"],"Completed":"Incomplete"}))
    return render_template('update-profile-inprogress.html', username=username, edit=edit, goals=goal,files=file)
    
@app.route('/delete-goal-inprogress/<username>_<goal_id>')
def deletegoalinprogress(goal_id, username):
    mongo.db.Goals.remove({'_id': ObjectId(goal_id)})
    return redirect(url_for('profileinprogress', username=username,files=file))


@app.route('/updated-inprogressgoal/<username>_<goal_id>', methods=['POST'])
def updategoalinprogress(goal_id, username):
    edit = mongo.db.Goals.find_one({'_id': ObjectId(goal_id)})
    if not request.form['Details']:
        details = edit["Details"]
    else:
        details = request.form['Details']
    updates = {
             'user': session["user"],
             "Date": edit['Date'],
             'Title': request.form['Title'],
             'Details': details,
             'Completed': request.form['Completed']
        }
    mongo.db.Goals.update({"_id": ObjectId(goal_id)}, updates)
    return redirect(url_for('profileinprogress', username=username,files=file))






@app.route('/edit-profilepicture/<username>')
def editprofilepicture(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    goal = list(mongo.db.Goals.find({"user": session["user"]}))
    return render_template('update-profilepicture.html', username=username,goals=goal,files=file)

@app.route('/edit-profilepicture-completed/<username>')
def editprofilepicturecompleted(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    goal = list(mongo.db.Goals.find({"user": session["user"],"Completed":"Complete"}))
    return render_template('update-profilepicture-completed.html', username=username,goals=goal,files=file)

@app.route('/edit-profilepicture-inprogress/<username>')
def editprofilepictureinprogress(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    goal = list(mongo.db.Goals.find({"user": session["user"],"Completed":"Incomplete"}))
    return render_template('update-profilepicture-inprogress.html', username=username,goals=goal,files=file)

@app.route("/search-workouts", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    workout = list(mongo.db.Workouts.find({"$text": {"$search": query}}))
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    return render_template("workouts.html", username=username,files=file, workouts=workout)



@app.route("/MyWorkouts-difficulty-1/<username>", methods=["GET", "POST"])
def workouts1(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    workout = list(mongo.db.Workouts.find({"user": session["user"],"Difficulty":"One"}))
    return render_template("workouts.html", username=username,files=file, workouts=workout)

@app.route("/MyWorkouts-difficulty-2/<username>", methods=["GET", "POST"])
def workouts2(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    workout = list(mongo.db.Workouts.find({"user": session["user"],"Difficulty":"Two"}))
    return render_template("workouts.html", username=username,files=file, workouts=workout)

@app.route("/MyWorkouts-difficulty-3/<username>", methods=["GET", "POST"])
def workouts3(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    workout = list(mongo.db.Workouts.find({"user": session["user"],"Difficulty":"Three"}))
    return render_template("workouts.html", username=username,files=file, workouts=workout)

@app.route("/MyWorkouts-difficulty-4/<username>", methods=["GET", "POST"])
def workouts4(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    workout = list(mongo.db.Workouts.find({"user": session["user"],"Difficulty":"Four"}))
    return render_template("workouts.html", username=username,files=file, workouts=workout)
    
@app.route("/MyWorkouts-difficulty-5/<username>", methods=["GET", "POST"])
def workouts5(username):
    file = list(mongo.db.files.find({"id": session["user"]}))
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    workout = list(mongo.db.Workouts.find({"user": session["user"],"Difficulty":"Five"}))
    return render_template("workouts.html", username=username,files=file, workouts=workout)



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)