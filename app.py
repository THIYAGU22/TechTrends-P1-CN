import sqlite3

from flask import Flask, json, render_template, request, url_for, redirect, flash
import logging
from sqlite3 import Error

from constants import *

app = Flask(__name__)

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global DB_CONNECTION_COUNT
    try:
        connection = sqlite3.connect(DB_CONNECTION_STRING,uri=True)
        connection.row_factory = sqlite3.Row
        DB_CONNECTION_COUNT += 1
        return connection
    except Error:
        app.logger.critical('DB MISSING : check DB %s exists', DB_CONNECTION_STRING)
        return None

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post

# Define the main route of the web application
@app.route('/')
def index():
    global POSTS_COUNT
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    POSTS_COUNT = len(posts)
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.error("Post id : %s missing",post_id)
        return render_template('404.html'), 404
    else:
        app.logger.info("Post id : %s retrieved",post_id)
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info("About Us Page retrieved")
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    global POSTS_COUNT
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            POSTS_COUNT += 1
            app.logger.info('New Post : %s created',POSTS_COUNT)
            return redirect(url_for('index'))
    return render_template('create.html')

# application metrics logging
# TODO : /metrics endpoint to keep track of "db_connection_count" & "post_count"
@app.route('/metrics')
def metrics():
    data = {
        "db_connection_count": DB_CONNECTION_COUNT,
        "post_count":  POSTS_COUNT,
    }
    response = app.response_class(
        response=json.dumps(data),
        status=OK_RESPONSE_CODE,
        mimetype=APPLICATION_CONTENT_TYPE
    )
    app.logger.info('Status request successfull : %s', data)
    return response

# Health logging
# TODO : /healthz dynamic endpoint to notify whether DB exists
@app.route('/healthz')
def healthcheck():
    conn = get_db_connection()
    response_code = OK_RESPONSE_CODE
    data = {
        "DB_FILE": FILE_FOUND,
        "result": OK_RESPONSE_STATUS
    }

    if(conn is None):
        response_code = ISERROR_RESPONSE_CODE
        data["DB_FILE"] = FILE_NOT_FOUND
        data["result"] = ERROR_RESPONSE_STATUS

    response = app.response_class(
        response=json.dumps(data),
        status=response_code,
        mimetype=APPLICATION_CONTENT_TYPE
    )
    app.logger.info('Status request successfull %s', data["result"])
    return response


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run(host='0.0.0.0', port='3111')
