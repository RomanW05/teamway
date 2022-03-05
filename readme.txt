Understanding the structure from which app.py is based upon:
    A worker has shifts
    A shift is 8 hours long
    A worker never has two shifts on the same day
    It is a 24-hour timetable 0-8, 8-16, 16-24

Assumptions:
- The worker can choose which shift he/she wants to do in one day
- The worker can modify already selected shifts
- The company selects how many days in advance a worker can select his/her schedule
- The worker can create and modify his/her schedule up to "x" days in advance

Based on these parameters the company must have:
- A calendar
- A record of all workers (usernames and passwords)
- A record of the selected shifts per day per worker

Restrictions:
- Within one calendar day one worker can only do one shift
- There are only three shifts available per day:
    Night:      0-8
    Morning:    8-16
    Afternoon:  16-24
- The worker cannot modify past shifts

REST API logic:
To insert one working shift, the worker must be logged in and then choose an available slot


Dataflow:

From the worker's point of view, the worker:
1. Logs in
2. Selects one day of the calendar
3. Selects one shift
4. Submits the selected shift
5. Logs out

From the back-end point of view, the server:
1. Receives a username and a password
    a.  Compares the username and password with the stored one in the database
    b.  If success:
            Waits for more user input
        If fails:
            Sends the user back to the login menu and displays an error
2. Receives one shift and one date from one user
3. Creates a list of available dates from which the worker can pick 
    Cases:
    a.  The selected date is not included in the database:
            Insert that shift in the database
    b.  The selected date is already included in the database:
            Modify the shift of that date
    c.  The selected date is out of range "x" days in advance:
            Return and make the user select a new date again
4. Logs out the user automatically after 30 minutes of the session
5. Logs out the user if he/she logs out manually
6. Registers a new user
    a. Stores the password as an encoded hash and salt to keep the user safer in case of a database leak
    b. Stores the username in plain text

From the front-end point of view, the website:
1. login.html displays:
    a. A login menu 
    b. A registration menu
2. schedule.html page displays:
    a. A calendar picker
    b. Shifts to be selected (Morning shift preselected)
    c. Logout button
Note: Header and footer are stored as a 'variable' for the back-end to display in every page. There is room in every page to include <title>, <style>,... tags in the corresponding <head> before the closing brakets </head> for HTML5 protocol and SEO purposes. Same applies to JavaScript scripts before </head> (header) and before </html> (footer) tags


The database:
It has human readiable parameters for the administration crew to easily check some workers information. The database has two tables: 
    1. Shifts
        a. Day  # The day the worker wants to do the job
        b. Shift  # Hardcoded parameters based on requirements (Night: 0-8, Morning: 8-16, Afternoon: 16-24)
        c. Username
    2. Workers
        a. Username
        b. Password


Unit tests:
    Go to the tests route and from there run the tests directly calling python and the 'test.py' script
