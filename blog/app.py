import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

"""This get_db_connection() function opens a connection to the database.db database file, and then sets the row_factory attribute to sqlite3.Row. 
The database connection will return rows that behave like regular Python dictionaries. Function returns the conn connection object be using to access the database."""


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


"""Inside the function, use get_db_connection() function to open a database connection and execute a SQL query to get the blog post associated with the given post_id value. 
Add the fetchone() method to get the result and store it in the post variable then close the connection. 
If the post variable has the value None, meaning no result was found in the database, use the abort() function imported earlier to respond with a 404 error code"""


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


app = Flask(__name__)
#import secerts and run secrets.token_hex(16) in terminal 
app.config["SECRET_KEY"] = "f8f9c3253a3995f26c7586d36f2ca02d"


@app.route("/")
def index():
    """first open a database connection using the get_db_connection() functionMdefined earlier. Then execute an SQL query to select all entries from the posts table.
    implement the fetchall() method to fetch all the rows of the query result, this will return a list of the posts inserted into the database in the previous step."""
    conn = get_db_connection()
    posts = conn.execute("SELECT * FROM posts").fetchall()
    conn.close()
    return render_template("index.html", posts=posts)


@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    return render_template("post.html", post=post)


@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO posts (title, content) VALUES (?, ?)", (title, content)
            )
            conn.commit()
            conn.close()
            
            return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        if not title:
            flash("Title is required!")
        else:
            conn = get_db_connection()
            conn.execute(
                "UPDATE posts SET title = ?, content = ?" " WHERE id = ?",
                (title, content, id),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("index"))

    return render_template("edit.html", post=post)


@app.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post["title"]))
    return redirect(url_for("index"))


app.run("0.0.0.0", debug=True)
