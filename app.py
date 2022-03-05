from flask import *
from flask_session import Session
import sqlite3
import bcrypt
from datetime import date, timedelta, datetime
import os.path


#App start
app = Flask(__name__, template_folder='templates')

# App configuration parameters
app.config["SESSION_COOKIE_SECURE"] = True,
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"]= 1800  # Seconds. 30 min session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TESTING'] = True
app.config['DEBUG'] = True
app.config['BASEDIR'] = os.path.dirname(os.path.abspath(__file__))
app.secret_key = 'Session_Secret_Key'

Session(app)

# Data to be modified at will
days_ahead = 30


def current_path(name):
    # Sets the full path of any file within this level
    db_path = os.path.join(app.config['BASEDIR'], name)

    return db_path


def range_dates(days_ahead):
    # Retrieves a consecutive list of days "days_ahead"
    todays_date = datetime.now()  # type datetime.datetime

    available_days = []
    for x in range(days_ahead + 1):
        td = timedelta(x) 
        single_day = todays_date + td
        available_days.append(single_day.strftime('%Y-%m-%d'))

    return available_days


# Routes
@app.route('/')
def index():
    # Root
    return render_template('/login.html')


@app.route('/check_username', methods=['GET', 'POST'])
def check_username():
    # Check username credentials
    if request.method == "POST":

        # Receive username and password from the website
        username = request.form['username']
        password = request.form['password'].encode()

        # Fetch username and password from the database
        with (sqlite3.connect(current_path("company_info.db"))) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM workers WHERE username = ?''', (username,))
            result = cursor.fetchone()
            conn.commit()

        # Incorrect username and password
        if result == None:
            return render_template('/login.html', error='Wrong username or password. Please try again') 

        stored_username = result[0]
        stored_password = result[1].encode()

        # Check if passwords match one another
        if bcrypt.checkpw(password, stored_password):
            session['username'] = username

            return render_template('/schedule.html', username=username)
        else:
            return render_template('/login.html', error='Wrong username or password')
    return render_template('/login.html', error='Wrong username or password')


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    # In order to select a date and shift the user must be logged in
    if not session.get('username'):
        return render_template('/login.html', error='Please, login first')

    return render_template('/schedule.html')


@app.route('/add_shift', methods=['GET', 'POST'])
def add_shift():
    # Adds or modifies a shift from a worker into the database
    # In order to select a date and shift the user must be logged in
    if not session.get('username'):
        return render_template('/login.html', error='Please, login first')

    if request.method == "POST":

        # Fetch data from the website
        username = session['username']
        selected_day = request.form['day']
        shift = request.form['options']

        if selected_day == '':
            return render_template('/schedule.html', message=f'Please, select any day from today until {days_ahead} days ahead')

        if shift == '':
            return render_template('/schedule.html', message=f'Please, select a shift')

        # Format the day to fetch from the database
        selected_day = datetime.strptime(selected_day, '%Y-%m-%d')
        selected_day = datetime.strftime(selected_day, '%Y-%m-%d')

        # Load all relevant info about the workers shift
        with(sqlite3.connect(current_path("company_info.db"))) as conn:

            # Change results from tupple to list for easier search
            conn.row_factory = lambda cursor, row: row[0]
            cursor = conn.cursor()
            cursor.execute('''SELECT * FROM shifts WHERE username = ?''', (username,))
            results = cursor.fetchall()

            # Create list of available days
            available_days = range_dates(days_ahead)

            # Make changes in the database acordingly
            if ((selected_day in available_days) and (selected_day not in results)):
                cursor.execute('''INSERT INTO shifts (shift, day, username) VALUES (?, ?, ?)''', (shift, selected_day, username))
                conn.commit()

                return render_template('/schedule.html', message=f'Success! You will work the day {selected_day} on the {shift} shift. Please, select another day')
            
            elif ((selected_day in available_days) and (selected_day in results)):
                cursor.execute('''UPDATE shifts set shift = ? WHERE day = ? and username = ?''', (shift, selected_day, username))
                conn.commit()

                return render_template('/schedule.html', message=f'Success! You now work the shift {shift} on the day {selected_day}. Please, select another day')
            
            else:
                return render_template('/schedule.html', message=f'Please, select any day from today until {days_ahead} days ahead')

    return render_template('/schedule.html', message='Please, select a day and a shift you would like to work')


@app.route('/user_registration', methods=['GET', 'POST'])
def user_registration():
    if request.method == "POST":

        # Fetch data from the website
        username = request.form['username']
        password = request.form['password'].encode()

        # Encode password for security reasons
        hashed = bcrypt.hashpw(password, bcrypt.gensalt(rounds=16))
        hashed = hashed.decode('utf-8')

        with (sqlite3.connect(current_path("company_info.db"))) as conn:
            cursor = conn.cursor()

            # Before inserting a new user, make sure the user does not already exist
            cursor.execute('''SELECT * FROM workers WHERE username = ?''', (username,))
            result = cursor.fetchone()
            if result != None:
                return render_template('/login.html', error='User already exists')
            conn.commit()

            cursor.execute('''INSERT INTO workers (username, password) VALUES (?, ?)''', (username, hashed))
            conn.commit()

        return render_template('/login.html', error='Success! New user added. Please, login to continue')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if not session.get('username'):
        return render_template('/login.html')

    # Clean session
    session.pop('username', None)
    return render_template('/login.html')

if __name__ == '__main__':
    app.run(debug=True)
