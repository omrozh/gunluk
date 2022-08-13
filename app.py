import flask
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from datetime import datetime
import base64
from jinja2 import Environment, FileSystemLoader
from flask_mail import Mail, Message


app = flask.Flask(__name__)
app.config["SECRET_KEY"] = "lets_try_this_shit_too_what_do_we_have_to_lose"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"


db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.yandex.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'no-reply@inadsglobal.com'
app.config['MAIL_PASSWORD'] = '05082004Oo'
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


class Subscriber(db.Model):
    id = db.Column(db.String, primary_key=True)
    subscribed_date = db.Column(db.Date)
    email = db.Column(db.String)


class Story(db.Model):
    id = db.Column(db.String, primary_key=True)
    story_date = db.Column(db.Date)
    title = db.Column(db.String)
    content = db.Column(db.String)
    image_content = db.Column(db.String)
    long_content = db.Column(db.String)


def generate_email():
    env = Environment(loader=FileSystemLoader('email_templates'))
    template = env.get_template("email_template.html")
    output_from_parsed_template = template.render(articles=Story.query.filter_by(story_date=datetime.today().date()).all())
    return output_from_parsed_template


def send_daily_emails():
    msg = Message("Günlük Bülteniniz",
                  sender="no-reply@inadsglobal.com",
                  recipients=[i.email for i in Subscriber.query.all()])

    msg.html = generate_email()
    mail.send(msg)


@app.route("/", methods=["POST", "GET"])
def index():
    if flask.request.method == "POST":
        new_subscriber = Subscriber(id=str(uuid4()), email=flask.request.values["email"],
                                    subscribed_date=datetime.today())
        db.session.add(new_subscriber)
        db.session.commit()
        return flask.render_template("confirm-signup.html")
    return flask.render_template("index.html")


@app.route("/assets/<file_name>")
def assets(file_name):
    return flask.send_file("assets/" + file_name)


@app.route("/admin/<username>/<password>", methods=["POST", "GET"])
def admin(username, password):
    if username == "omrozh" and password == "05082004Oo":
        if flask.request.method == "POST":
            image_file = flask.request.files["story_image"]
            image_file.save("story_images/" + image_file.filename)

            with open("story_images/" + image_file.filename, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read())

            values = flask.request.values

            new_story = Story(id=str(uuid4()), title=values["title"], story_date=datetime.today(),
                              content=values["content"], image_content=encoded_string)
            db.session.add(new_story)
            db.session.commit()
        return flask.render_template("admin.html")


@app.route("/admin-send-mail/<user>/<password>")
def admin_send_mail(user, password):
    if user == "omrozh" and password == "05082004Oo":
        send_daily_emails()
        return flask.redirect("/")
