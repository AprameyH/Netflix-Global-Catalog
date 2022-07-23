""" Specifies routing for the application"""
from os import uname
from flask import redirect, render_template, request, jsonify
from app import app
from app import database as db_helper

#GLOBAL VARIABLES
log_in = "False"
username = "USER"

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
    """ returns rendered homepage """
    items = db_helper.fetch_countries()
    return render_template("index.html", items=items)

@app.route("/account")
def accountpage():
    global log_in

    if log_in == "False":
        return redirect("/login")
    
    items = db_helper.fetch_countries()
    return render_template("account.html", items=items, username = username)

@app.route("/login", methods=['GET', 'POST'])
def loginpage():
    global log_in
    global username
    """ displays login page and gets email """
    log_in = False
    if request.method =='POST':
        if len(request.form['uemail']) != 0 and request.form['uemail'].find("@") != -1:
            
            username = request.form['uname']
            log_in = "True"
            
            return redirect("/account")
        else:
            log_in = "False"
            return render_template("login.html", error="Please enter a valid email")
            
    return render_template("login.html", error="")
    
