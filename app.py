import hmac
import sqlite3
import datetime
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_mail import Mail, Message
# import sentry_sdk
#
# sentry_sdk.init(
#     "https://<key>@sentry.io/<project>",
#
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for performance monitoring.
#     # We recommend adjusting this value in production.
#     traces_sample_rate=1.0,




class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def fetch_users():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[1], data[2], data[4]))
    return new_data


def fetch_shop():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM shop")
        cart = cursor.fetchall()

        new_data = []

        for data in cart:
            new_data.append(Cart(data[1], data[2], data[3], data[4]))
    return new_data


users = fetch_users()


def init_user_table():
    conn = sqlite3.connect('users.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "username TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


def init_shop():
    with sqlite3.connect('users.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS shop (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "product_type TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "product_quantity TEXT NOT NULL)")
    print("product table created successfully.")


class Cart(object):
    def __init__(self, product_name, product_type, price, product_quantity):
        self.product_name = product_name
        self.product_type = product_type
        self.price = price
        self.product_quantity = product_quantity


def fetch_products():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT *FROM product")
        products = cursor.fetchall()

        new_data = []

        for data in products:
            new_data.append(Cart(data[1], data[2], data[3], data[4]))
    return new_data


init_user_table()
init_shop()

username_table = { u.username: u for u in users }
userid_table = { u.id: u for u in users }


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kiyaamudienkhan@gmail.com'
app.config['MAIL_PASSWORD'] = 'Khanget47'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":

        username = request.form['username']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "username,"
                           "last_name,"
                           "email,"
                           "password) VALUES(?, ?, ?, ?)", (username, last_name, email, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
            msg = Message('Hello Message', sender='kiyaamudienkhan@gmail.com',
                          recipients=[email])
            msg.body = 'My email using Flask'
            mail.send(msg)
        return response


# @app.route('/create-users/', methods=["POST"])
# @jwt_required()
# def create_users():
#     response = {}
#
#     if request.method == "POST":
#         title = request.form['title']
#         content = request.form['content']
#         date_created = datetime.datetime.now()
#
#         with sqlite3.connect('users.db') as conn:
#             cursor = conn.cursor()
#             cursor.execute("INSERT INTO post("
#                            "title,"
#                            "content,"
#                            "date_created) VALUES(?, ?, ?)", (title, content, date_created))
#             conn.commit()
#             response["status_code"] = 201
#             response['description'] = "users cart added succesfully"
#         return response


@app.route('/get-users/<int:id>', methods=["GET"])
def get_users(id):
    response = {}
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE user_id=" + str(id))
        response['status_code'] = 200
        response['data'] = cursor.fetchone()
    return jsonify(response)


@app.route("/delete-product/<int:post_id>")
@jwt_required()
def delete_product(product_id):
    response = {}
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM shop WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "users product deleted successfully."
    return response


@app.route('/edit-cart/<int:product_id>', methods=["PUT"])
def edit_cart(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('users.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("product_name") is not None:
                put_data["product_name"] = incoming_data.get("product_name")
                with sqlite3.connect('users.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE shop SET product_name =? WHERE id=?", (put_data["product_name"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully added"
                    response['status_code'] = 200
                return response
            if incoming_data.get("product_type") is not None:
                put_data['product_type'] = incoming_data.get('content')

                with sqlite3.connect('users.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE shop SET product_type =? WHERE id=?", (put_data["product_type"], product_id))
                    conn.commit()

                    response["product_type"] = "Cart updated successfully"
                    response["status_code"] = 200
                return response
            if request.method == "PUT":
                with sqlite3.connect('users.db') as conn:
                    incoming_data = dict(request.json)
                    put_data = {}

                    if incoming_data.get("product_quantity") is not None:
                        put_data["product_quantity"] = incoming_data.get("product_quantity")
                        with sqlite3.connect('users.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE shop SET product_quantity =? WHERE id=?",
                                           (put_data["product_quantity"], product_id))
                            conn.commit()
                            response['message'] = "Update was successfully added"
                            response['status_code'] = 200
                        return response
                    if incoming_data.get("product_quantity") is not None:
                        put_data['product_quantity'] = incoming_data.get('content')

                        with sqlite3.connect('users.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute("UPDATE shop SET product_quantity =? WHERE id=?",
                                           (put_data["product_quantity"], product_id))
                            conn.commit()

                            response["product_quantity"] = "Cart updated successfully"
                            response["status_code"] = 200
                        return response
            return response
    return response


@app.route('/get-user/<int:post_id>/', methods=["GET"])
def get_user(post_id):
    response = {}

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM post WHERE id=" + str(post_id))

        response["status_code"] = 200
        response["description"] = "users retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


@app.route('/products/', methods=["POST"])
def products():
    response = {}

    if request.method == "POST":

        product_name = request.form['product_name']
        product_type = request.form['product_type']
        price = request.form['price']
        product_quantity = request.form['product_quantity']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shop("
                           "product_name,"
                           "product_type,"
                           "price,"
                           "product_quantity) VALUES(?, ?, ?, ?)", (product_name, product_type, price, product_quantity))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


if __name__ == '__main__':
    app.run()
