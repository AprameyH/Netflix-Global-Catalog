"""Defines all the functions related to the database"""
from asyncio import QueueEmpty
from app import db
import random

def fetch_movies(country="All") -> dict:
    """Reads all tasks listed in the todo table

    Returns:
        A list of dictionaries
    """

    conn = db.connect()
    if country == "All":
        query_results = conn.execute("SELECT name, media_type, synopsis FROM Movie LIMIT 100;").fetchall()
    else:
        countryfilter = 'SELECT name, media_type, synopsis FROM (SELECT movie_id, country_name FROM Movie M NATURAL JOIN Availability A NATURAL JOIN Country C WHERE country_name = "{}") AS T NATURAL JOIN Movie M ORDER By name LIMIT 100'.format(country)
        query_results = conn.execute(countryfilter)
        
    conn.close()
    todo_list = []
    for result in query_results:
        item = {
            "name": result[0],
            "media_type": result[1],
            "synopsis": result[2]
        }
        todo_list.append(item)

    return todo_list


def fetch_countries():

    conn = db.connect()
    query_results = conn.execute('SELECT country_name FROM Country WHERE (country_name NOT LIKE "___") AND (country_name NOT LIKE "__") ORDER by country_name;').fetchall()
    conn.close()
    country_list = []
    for result in query_results:
        country_list.append(result[0])
    
    return country_list


def search_movies(input, current_email, country="All") -> dict:
    """Reads all tasks listed in the todo table

    Returns:
        A list of dictionaries
    """
    

    conn = db.connect()

    if country != "All":
        advanced_query2 = 'SELECT movie_id, name, media_type, synopsis, country_name FROM (SELECT movie_id, country_name FROM Movie M NATURAL JOIN Availability A NATURAL JOIN Country C WHERE country_name = "{}") AS T NATURAL JOIN Movie M WHERE name LIKE "%%{}%%" ORDER By name;'.format(country, input)

        query_results = conn.execute(advanced_query2).fetchall()
    else:
        query2 = 'SELECT movie_id, name, media_type, synopsis, country_name FROM (SELECT movie_id, country_name FROM Movie M NATURAL JOIN Availability A NATURAL JOIN Country C) AS T NATURAL JOIN Movie M WHERE name LIKE "%%{}%%" ORDER By name;'.format(input)
        query_results = conn.execute(query2).fetchall()
    conn.close()

    
    
    todo_list = []
    for result in query_results:
        item = {
            "movie_id": result[0],
            "name": result[1],
            "media_type": result[2],
            "synopsis": result[3],
        }
        todo_list.append(item)

    if current_email != None and len(todo_list) != 0:
        conn = db.connect()

        query_results = conn.execute('SELECT user_id FROM User WHERE email ="{}";'.format(current_email)).fetchall()

        if len(query_results) == 0:
            conn.close()
            return []
        user_id = query_results[0][0]
        movie_id = todo_list[0]["movie_id"]

        search_insert ='INSERT INTO Search(user_id, search_text, movie_id) VALUES("{}", "{}", "{}")'.format(
            user_id, input, movie_id)

        conn.execute(search_insert)


        conn.close()
        
        connection = db.raw_connection()


        try:
            cursor = connection.cursor()
            cursor.callproc("addRecommend", [current_email])
            results = list(cursor.fetchall())
            cursor.close()
            print("Cursor called")
            connection.commit()
        finally:
            connection.close()

        print(results)
        # query = 'CALL addRecommend("{}")'.format(current_email)
        # query_results = conn.execute(query).fetchall()
        # print("Ran query", query_results)
        # conn.close()
    
    return todo_list


def recommend_movies(current_email) -> dict:
    # We first need the director name and the movie name of the most recently searched movie
    # Check if Logged In
    if current_email == None:
        return []


    conn = db.connect()

    # Get user_id
    query_results = conn.execute(
        'SELECT user_id FROM User WHERE email ="{}";'.format(current_email)).fetchall()
    print('SELECT user_id FROM User WHERE email ="{}";'.format(current_email))
    user_id = query_results[0][0]
    
    # Get recos from table
    query_results = conn.execute(
        'SELECT R.movie_name, R.movie_type, R.movie_synopsis FROM Recommendation R RIGHT JOIN(SELECT DISTINCT movie_name FROM Recommendation WHERE user_id={}) subq ON R.movie_name=subq.movie_name ORDER By R.recommendation_id DESC LIMIT 100'.format(user_id)).fetchall()

    conn.close()

    if len(query_results) == 0:
        return []

    rec_list = []
    for result in query_results:
        item = {
            "name": result[0],
            "media_type": result[1],
            "synopsis": result[2]
        }
        rec_list.append(item)
    return rec_list

def update_task_entry(task_id: int, text: str) -> None:
    """Updates task description based on given `task_id`

    Args:
        task_id (int): Targeted task_id
        text (str): Updated description

    Returns:
        None
    """

    conn = db.connect()
    query = 'Update tasks set task = "{}" where id = {};'.format(text, task_id)
    conn.execute(query)
    conn.close()


def update_status_entry(task_id: int, text: str) -> None:
    """Updates task status based on given `task_id`

    Args:
        task_id (int): Targeted task_id
        text (str): Updated status

    Returns:
        None
    """

    conn = db.connect()
    query = 'Update tasks set status = "{}" where id = {};'.format(text, task_id)
    conn.execute(query)
    conn.close()

# def insert_new_task(text: str) -> int
def insert_new_movie(name: str, synop: str) ->  int:
    """Insert new task to todo table.

    Args:
        text (str): Task description

    Returns: The task ID for the inserted entry
    """

    conn = db.connect()
    #query = 'Insert Into tasks (task, status) VALUES ("{}", "{}");'.format(
    #    text, "Todo")
    query = 'INSERT INTO Movie (movie_id, name, media_type, synopsis) VALUES ("{}", "{}", "{}", "{}");'.format(
        random.randint(10000000,99999999), name, "movie", synop) # now need to change part of routes.py
    conn.execute(query)
    query_results = conn.execute("Select LAST_INSERT_ID();")
    query_results = [x for x in query_results]
    task_id = query_results[0][0]
    conn.close()

    return task_id


def insert_new_user(name: str, email: str) -> int:
    """Insert new task to todo table.

    Args:
        text (str): Task description

    Returns: The task ID for the inserted entry
    """

    conn = db.connect()
    #query = 'Insert Into tasks (task, status) VALUES ("{}", "{}");'.format(
    #    text, "Todo")
    count_q = 'SELECT COUNT(*) FROM User WHERE email LIKE "{}";'.format(email)
    count = (conn.execute(count_q).fetchall())
    count = count[0][0]
    

    if count == 0:
 
        query = 'INSERT INTO User (username, email) VALUES ("{}", "{}");'.format(
        name, email)  # now need to change part of routes.py
        conn.execute(query)


    conn.close()

    return 200


def update_user(oldemail: str, name: str, email: str) -> int:
    """Insert new task to todo table.

    Args:
        text (str): Task description

    Returns: The task ID for the inserted entry
    """

    conn = db.connect()
    count_q = 'SELECT COUNT(*) FROM User WHERE email LIKE "{}";'.format(oldemail)
    count = (conn.execute(count_q).fetchall())
    count = count[0][0]
    if count == 0:
        conn.close()
        return 404
    
    count_q = 'SELECT COUNT(*) FROM User WHERE email LIKE "{}";'.format(email)
    countnew = (conn.execute(count_q).fetchall())
    countnew = countnew[0][0]
    
    if countnew != 0:
        conn.close()
        return 300
    
    query = 'UPDATE User SET username = "{}", email = "{}" WHERE email LIKE "{}";'.format(
        name, email, oldemail)
    
    conn.execute(query)


    conn.close()

    return 200

def delete_user(username: str, email: str):

    conn = db.connect()

    query = 'DELETE FROM User WHERE username = "{}" AND email = "{}";'.format(username, email)

    conn.execute(query)


    conn.close()

    return 200


def remove_task_by_id(task_id: int) -> None:
    """ remove entries based on task ID """
    conn = db.connect()
    query = 'Delete From tasks where id={};'.format(task_id)
    conn.execute(query)
    conn.close()

