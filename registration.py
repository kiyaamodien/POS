import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity


class User(object):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.email = email
        self.password = password


def fetch_users():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[1], data[2], data[3], data[4]))
    return new_data

# users = fetch_users()

def init_user_table():
    conn = sqlite3.connect('users.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()

init_user_table()

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "first_name,"
                           "last_name,"
                           "email,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, email, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response

if __name__ == '__main__':
    app.run(debug=True)