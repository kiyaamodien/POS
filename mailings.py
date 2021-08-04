from flask import Flask
from flask_mail import Mail, Message


app = Flask(__name__)

app.config['MAIL_SERVER'] ='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kiyaamudienkhan@gmail.com'
app.config['MAIL_PASSWORD'] = 'Khanget47'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route('/')
def index():
    msg = Message('Hello Message', sender='kiyaamudienkhan@gmail.com',
recipients=['mujaid.kariem22@gmail.com'])
    msg.body = 'My email using Flask'
    mail.send(msg)
    return "Message send"


if __name__ == '__main__':
    app.debug = True
    app.run()
