from flask import Flask,render_template,flash, redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import datetime
from validate_email import validate_email

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

mail = Mail(app)

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])


class Contestant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    year_of_birth = db.Column(db.Integer)
    telephone = db.Column(db.String(25))
    club = db.Column(db.String(50))
    contest = db.Column(db.String(25))
    confirmation = db.Column(db.String())
    time = db.Column(db.DateTime(), default=datetime.datetime.now())
    active = db.Column(db.Boolean(), default=False)
    ip = db.Column(db.String(16))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        token = s.dumps(email, salt='email-confirm')
        validation = validate_email(email, verify=True)
        
        new_contestant = Contestant(first_name = request.form['firstname'], last_name = request.form['lastname'], 
        email = request.form['email'], telephone = request.form['telephone'],
        year_of_birth = request.form['yob'], contest = request.form['contest'], confirmation=token,
        gender = request.form['gender'],club = request.form['club'], ip = request.environ['REMOTE_ADDR'])

        msg = Message('Email confirmation', sender='kretko1994@gmail.com', recipients=[email])
        link = url_for('confirm_email', token=token, _external=True)
        msg.body = 'Please confirm your registration on this link: {}'.format(link)

        if validation == True:
            mail.send(msg)
            db.session.add(new_contestant)
            db.session.commit()
        else:
            return '<h3>Email is invalid</h3>'

        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=79200)
    except SignatureExpired:
        return '<h1>Confirmation time has expired</h1>'
    
    return '<h1>Registration confirmed successfully!</h1>'

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)