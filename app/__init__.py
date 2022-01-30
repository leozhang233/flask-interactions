# to run this website and watch for changes: 
# $ export FLASK_ENV=development; flask run

from flask import Flask, g, render_template, request
import pandas as pd
import sqlite3
import io
import base64

# Create web app, run with flask run
# (set "FLASK_ENV" variable to "development" first!!!)

app = Flask(__name__)

@app.route('/')
# Create main page (fancy)
def main():
    return render_template('main_better.html')

# Show url matching
# Page with form

@app.route('/submit/', methods=['POST', 'GET'])
def submit():
    if request.method == 'GET':
        return render_template('submit.html')
    else:
        try:
            insert_message(request)
            return render_template('submit.html', thanks = True)
        except:
            return render_template('submit.html', error=True)

def get_message_db():
    # check whether there is a database called message_db in the 
    # g attribute of the app
    if 'message_db' not in g:
        g.message_db = sqlite3.connect("messages_db.sqlite")

    cursor = g.message_db.cursor()
    # check whether a table called messages exists in message_db,
    # and create it if not
    cmd = \
        """
        CREATE TABLE IF NOT EXISTS messages (
            id integer,
            handle text,
            message text);
        """
    cursor.execute(cmd)
    # return the connection
    return g.message_db

def insert_message(request):
    # access the database
    g.message_db = get_message_db()
    cursor = g.message_db.cursor()
    # extract message and handle from request
    message = request.form["message"]
    handle = request.form["handle"]
    
    # ensure that the ID number of each message is unique
    mycursor = cursor.execute('select * from messages;')
    results = mycursor.fetchall()
    id = len(results) + 1
    
    # insert id, message and handle to the database
    cmd = \
        """
        INSERT INTO messages (id, handle, message)
        VALUES ({id}, '{handle}', '{message}')
        """.format(id = id, handle = handle, message = message)

    cursor.execute(cmd)
    # ensure that the row insertion has been saved
    g.message_db.commit()
    # close the connection
    g.message_db.close()

def random_messages(n):
    # access the database
    g.message_db = get_message_db()
    # select 5 random messages or fewer if necessary
    cmd = \
        """
        SELECT * FROM messages
        ORDER BY RANDOM()
        LIMIT {n}
        """.format(n = n)

    df = pd.read_sql_query(cmd, g.message_db)
    # close the connection
    g.message_db.close()
    return df

@app.route('/view/')
def view():
    try:
        ran_messages = random_messages(5)
        return render_template('view.html', ran_messages = ran_messages)
    except:
        return render_template('view.html', error=True)