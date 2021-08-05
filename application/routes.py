from application import app, db_connection
from flask import render_template, request, session, flash, redirect
from bson.json_util import dumps
import json
import datetime

connection_db = db_connection.db_connection()
db = connection_db.connect_to_mongodb()


@app.route("/")
def home():
    if "email" in session:
        return render_template("index.html", home=True, isLoggedIn=True)
    return render_template("index.html", home=True)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'name' in request.form and 'username' in request.form and 'password' in request.form and 'age' in request.form and 'gender' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        age = int(request.form.get("age"))
        gender = request.form.get("gender")
        usersTable = db["users"]
        new_user = {"name": name, "username": username, "password": password, "age": age, "gender": gender,
                    "voted": False}
        try:
            usersTable.insert_one(new_user)
        except Exception as e:
            print("An exception occurred ::", e)
        return render_template("login.html", msg="User successfully created!!!", register=True)
    else:
        if request.method != 'GET':
            return render_template("register.html", msg="Please enter user details carefully!!!", register=True)
    return render_template("register.html", register=True)


@app.route("/logout")
def logout():
    session.clear()
    return render_template("index.html", home=True)


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = 'Please login to your account'
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        usersTable = db["users"]
        username_found = usersTable.find_one({"username": username})
        if username_found:
            username_val = username_found['username']
            password_val = username_found['password']
            if password == password_val:
                if username == "admin@gmail.com":
                    session["email"] = username_val
                    return render_template("admin_index.html", home=True, isLoggedIn=True)
                else:
                    session["email"] = username_val
                    return render_template("index.html", home=True, isLoggedIn=True)
            else:
                if "email" in session:
                    return render_template("index.html", home=True, isLoggedIn=True)
                msg = 'Wrong password'
                return render_template('login.html', msg=msg)
        else:
            msg = 'Username not found'
            return render_template('login.html', msg=msg)

    return render_template("login.html", login=True)


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if request.method == 'POST' and 'name' in request.form and 'username' in request.form and 'password' in request.form and 'age' in request.form and 'gender' in request.form:
        username = request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        age = int(request.form.get("age"))
        gender = request.form.get("gender")
        users_table = db["users"]
        udata = users_table.find_one({"username": session["email"]})
        user_filter = {'_id': udata['_id']}
        user_new_value = {"$set": {"name": name, "username": username, "password": password, "age": age, "gender": gender}}
        users_table.update(user_filter, user_new_value, True)

        user_detail = db['users']
        data = user_detail.find_one({"username": username})
        name = data['name']
        username = data['username']
        password = data['password']
        age = data['age']
        gender = data['gender']

        if "email" in session:
            return render_template("profile.html", profile=True, name=name, username=username, password=password,
                                   age=age, gender=gender, isLoggedIn=True, msg="User successfully updated!!!")
        return render_template("profile.html", profile=True, name=name, username=username, password=password, age=age,
                               gender=gender, msg="User successfully updated!!!")

    elif request.method != 'GET':
            return render_template("profile.html", msg="Please enter user details carefully!!!", profile=True)
    elif request.method != 'POST':
        user_detail = db['users']
        data = user_detail.find_one({"username": session["email"]})
        name = data['name']
        username = data['username']
        password = data['password']
        age = data['age']
        gender = data['gender']

        if "email" in session:
            return render_template("profile.html", profile=True, name=name, username=username, password=password, age=age, gender=gender, isLoggedIn=True)
        return render_template("profile.html", profile=True, name=name, username=username, password=password, age=age, gender=gender)

@app.route("/past_results")
def past_results():
    # election 2019
    e_2019 = db["election_year_2019"]
    e_2019_cursor = e_2019.find()
    e_2019_cursor_list = list(e_2019_cursor)
    e_2019_json = dumps(e_2019_cursor_list)
    e_2019_data = json.loads(e_2019_json)

    # election 2020
    e_2020 = db["election_year_2020"]
    e_2020_cursor = e_2020.find()
    e_2020_cursor_list = list(e_2020_cursor)
    e_2020_json = dumps(e_2020_cursor_list)
    e_2020_data = json.loads(e_2020_json)

    # election 2021
    e_2021 = db["election_year_2021"]
    e_2021_cursor = e_2021.find()
    e_2021_cursor_list = list(e_2021_cursor)
    e_2021_json = dumps(e_2021_cursor_list)
    e_2021_data = json.loads(e_2021_json)

    if "email" in session:
        return render_template("past_results.html", login=True, e_2019_data=e_2019_data, e_2020_data=e_2020_data,
                               e_2021_data=e_2021_data, isLoggedIn=True)
    return render_template("past_results.html", login=True, e_2019_data=e_2019_data, e_2020_data=e_2020_data,
                           e_2021_data=e_2021_data)


@app.route("/voteNow")
def voteNow():
    candidates = db["election_year_2021"]
    candidates_cursor = candidates.find()
    candidates_cursor_list = list(candidates_cursor)
    candidates_json_1 = dumps(candidates_cursor_list)
    candidates_json = json.loads(candidates_json_1)
    voting_open = validate_time()
    if "email" in session:
        return render_template("voteNow.html", login=True, candidates_json=candidates_json, voting_open=voting_open, isLoggedIn=True)
    return render_template("voteNow.html", login=True, candidates_json=candidates_json, voting_open=voting_open)


@app.route("/futureEvents")
def futureEvents():
    eventData = [{"eventName": "Staff Selection Voting !!!", "eventDesc": "This event is held by Service Staff Selecltion "
                                                                      "Commission and main objective to select "
                                                                      "eligible candidate.",
                  "location": "23 Banting crescent", "time": " 12:30pm"},
                 {"eventName": "Party Refreshment Treat !!!", "eventDesc": "We are happy to announce that we organizing "
                                                                        "Refreshment treat for all the party members "
                                                                        ",Please come and join "
                                                                        "eligible candidate.",
                  "location": "Steels Ave 203", "time": " 03:50pm"},
                 {"eventName": "Declaration of Voting Results !!!", "eventDesc": "Its a great news for all party members that"
                                                                        " voting results will be announce on this event. So most "
                                                                        " Welcome and good luck to all"
                                                                        "eligible candidate.",
                  "location": " Queen West 501", "time": " 02:20pm"}
                 ]
    return render_template("futureEvents.html", login=True, eventData=eventData)


@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if 'email' in session:
        email = session['email']
        users_table = db["users"]
        email_found = users_table.find_one({"username": email})
        if email_found:

            if email_found['voted']:
                flash("You have already voted!")
                return redirect('/voteNow')

            candidates_table = db["election_year_2021"]
            candidate_name = request.args.get('candidate')
            candidate_found = candidates_table.find_one({"name": candidate_name})

            if candidate_found:
                # Update vote count of the candidate
                vote_count = int(candidate_found['vote']) + 1
                candidate_filter = {'name': candidate_name}
                candidate_new_value = {"$set": {'vote': vote_count}}
                candidates_table.update_one(candidate_filter, candidate_new_value)

                # Update voting status of the user
                user_filter = {'username': email}
                user_new_value = {"$set": {'voted': True}}
                users_table.update_one(user_filter, user_new_value)
                flash("Thank you for your vote")
            else:
                flash("Candidate: " + candidate_name + " not found")

            return redirect('/voteNow')
        else:
            msg = 'Unknown user'
    msg = 'You need to login before voting'
    return render_template('login.html', msg=msg)


def validate_time():
    now_time = datetime.datetime.now()
    voting_schedule = db["voting_schedule"]
    schedule_cursor = voting_schedule.find()[0]
    start_time = schedule_cursor['start_time']
    end_time = schedule_cursor['end_time']
    if start_time <= now_time <= end_time:
        return True
    else:
        # Concluding voting
        max_vote = 0
        winner_name = ""
        candidates = db["election_year_2021"]
        candidates_cursor = candidates.find()
        for data in candidates_cursor:
            if int(data['vote']) > max_vote:
                max_vote = int(data['vote'])
                winner_name = data['name']
        candidate_filter = {'name': winner_name}
        candidate_new_value = {"$set": {'is_winner': True}}
        candidates.update_one(candidate_filter, candidate_new_value)
        return False


@app.route("/election_candidate", methods=['GET', 'POST'])
def election_candidate():
    if request.method == 'POST' and 'name' in request.form and 'age' in request.form and 'party' in request.form and 'gender' in request.form:
        name = request.form.get("name")
        age = int(request.form.get("age"))
        party = request.form.get("party")
        gender = request.form.get("gender")
        usersTable = db["election_year_2021"]
        new_user = {"name": name, "age": age, "is_winner": True, "party": party, "vote":0, "gender": gender}
        try:
            usersTable.insert_one(new_user)
        except Exception as e:
            print("An exception occurred ::", e)
        return render_template("election_candidate.html", msg="Candidate successfully created!!!", register=True, isLoggedIn=True)
    else:
        if request.method != 'GET':
            return render_template("election_candidate.html", msg="Please enter candidate details carefully!!!", register=True, isLoggedIn=True)
    return render_template("election_candidate.html", register=True, isLoggedIn=True)


@app.route("/create_events", methods=['GET', 'POST'])
def create_events():
    if request.method == 'POST' and 'eventName' in request.form and 'eventDesc' in request.form and 'location' in request.form and 'time' in request.form:
        eventName = request.form.get("eventName")
        eventDesc = request.form.get("eventDesc")
        location = request.form.get("location")
        time = request.form.get("time")
        eventsTable = db["events"]
        new_event = {"eventName": eventName, "eventDesc": eventDesc, "location": location, "time": time}
        try:
            eventsTable.insert_one(new_event)
        except Exception as e:
            print("An exception occurred ::", e)
        return render_template("create_events.html", msg="Event successfully created!!!", admin_index=True, isLoggedIn=True)
    else:
        if request.method != 'GET':
            return render_template("create_events.html", msg="Please enter events details carefully!!!", admin_index=True, isLoggedIn=True)
    return render_template("create_events.html", admin_index=True, isLoggedIn=True)


@app.route("/admin_index")
def admin_index():
    if "email" in session:
        return render_template("admin_index.html", admin_index=True, isLoggedIn=True)
    return render_template("admin_index.html", admin_index=True)
