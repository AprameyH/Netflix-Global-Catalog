""" Specifies routing for the application"""
from os import uname
from flask import redirect, render_template, request, jsonify
from app import app
from app import database as db_helper

#GLOBAL VARIABLES
log_in = False
current_username = None
current_email = None

@app.route("/delete/<int:task_id>", methods=['POST'])
def delete(task_id):
    """ recieved post requests for entry delete """

    try:
        db_helper.remove_task_by_id(task_id)
        result = {'success': True, 'response': 'Removed task'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)


@app.route("/edit/<int:task_id>", methods=['POST'])
def update(task_id):
    """ recieved post requests for entry updates """

    data = request.get_json()

    try:
        if "status" in data:
            db_helper.update_status_entry(task_id, data["status"])
            result = {'success': True, 'response': 'Status Updated'}
        elif "description" in data:
            db_helper.update_task_entry(task_id, data["description"])
            result = {'success': True, 'response': 'Task Updated'}
        else:
            result = {'success': True, 'response': 'Nothing Updated'}
    except:
        result = {'success': False, 'response': 'Something went wrong'}

    return jsonify(result)



@app.route("/create", methods=['POST'])
def create():
    """ recieves post requests to add new task """
    data = request.get_json()
    # db_helper.insert_new_task(data['description'])
    db_helper.insert_new_movie(data['name'], data['synop']) # now need to change part of modal.js
    result = {'success': True, 'response': 'Done'}
    return jsonify(result)


@app.route("/", methods=['GET', 'POST'])
def homepage():
    global log_in
    global current_email

    items = db_helper.fetch_movies()
    clist2 = db_helper.fetch_countries()
    
    if request.method == 'POST':
        selected_country = request.form["countrydropdown"]
        items2 = db_helper.fetch_movies(selected_country)
        input = request.form['searchBar']
        if input != None:
            print("Calling search movies")
            items2 = db_helper.search_movies(input, current_email, selected_country)
            print("Finished search movies")

        return render_template("index.html", items=items2, clist = clist2)

    return render_template("index.html", items=items, clist = clist2)

@app.route("/account")
def accountpage():
    global log_in
    global current_email
    if log_in == False:
        return redirect("/login")
    
    items = db_helper.recommend_movies(current_email)
    return render_template("account.html", items=items, username = current_username)

@app.route("/login", methods=['GET', 'POST'])
def loginpage():
    global log_in
    global current_username
    global current_email
    """ displays login page and gets email """
    log_in = False
    current_email = None
    if request.method =='POST':
        current_username = request.form['uname']
        current_email = request.form['uemail']
        
        if len(current_email.strip()) != 0 and current_email.find("@") != -1 and len(current_username.strip()) != 0:
            
            log_in = True
            db_helper.insert_new_user(current_username, current_email)
            return redirect("/account")
        else:
            log_in = False
            current_email = None
            return render_template("login.html", error="Please enter a valid email")
            
    return render_template("login.html", error="")
    

@app.route("/update", methods=['GET', 'POST'])
def updatepage():
    global log_in
    global current_username
    global current_email
    """ displays update page and gets email """
    if request.method =='POST':
        oldemail = request.form['oldemail']
        newname = request.form['newname']
        newemail = request.form['newemail']
        if len(newname.strip()) != 0 and len(newemail.strip()) != 0 and newemail.find("@") != -1:
            db_helper.update_user(oldemail, newname, newemail)
            return redirect("/account")
        
        else:
            return render_template("updateuser.html", error="Please enter a valid email")
            
    return render_template("updateuser.html", error="")


@app.route("/delete", methods=['GET', 'POST','DELETE'])
def deleteuser():
    global current_email
    global current_username

    if current_email != None and current_username != None:
        db_helper.delete_user(current_username, current_email)
    return redirect("/login")