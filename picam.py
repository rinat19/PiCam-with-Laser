from RPIO import PWM
import RPi.GPIO as GPIO
import atexit
from flask import Flask, render_template, request, session, redirect, url_for, render_template, flash

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

laser = 7

GPIO.setup(laser, GPIO.OUT)
GPIO.output(laser, 0)

app = Flask(__name__)

app.config.update(dict(
    DEBUG=False,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='123'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

# This function maps the angle we want to move the servo to, to the needed PWM value
def angleMap(angle):
    return int((round((1950.0 / 180.0), 0) * angle) + 550)

# Create a dictionary called pins to store the pin number, name, and angle
pins = {
    23: {'name': 'pan', 'angle': 90},
    #22: {'name': 'tilt', 'angle': 90}
}

# Create two servo objects using the RPIO PWM library
servoPan = PWM.Servo()
servoTilt = PWM.Servo()

# Setup the two servos and turn both to 90 degrees
servoPan.set_servo(23, angleMap(90))
#servoPan.set_servo(22, angleMap(90))


# Cleanup any open objects
def cleanup():
    servo.stop_servo(23)
    servo.stop_servo(22)


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


# Load the main form template on webrequest for the root page
@app.route("/picam")
def picam():
    # Create a template data dictionary to send any data to the template
    templateData = {
        'title': 'PiCam'
    }
    # Pass the template data into the template picam.html and return it to the user
    return render_template('picam.html', **templateData)


@app.route('/add')
def add_entry():
    #    if not session.get('logged_in'):
    #        abort(401)
    if not session.get('laser_on'):
        GPIO.output(laser, 1)
        session['laser_on'] = True
        print('Laser is on')
        flash('Laser is on')
        return redirect(url_for('picam'))
    elif session.get('laser_on'):
        GPIO.output(laser, 0)
        session.pop('laser_on', None)
        print('Laser is off')
        flash('Laser is off')
        return redirect(url_for('picam'))


@app.route('/video')
def video():
    #    if not session.get('logged_in'):
    #        abort(401)
    if not session.get('video_on'):
        session['video_on'] = True
        print('Video is on')
        flash('Video is on')
        return redirect(url_for('picam'))
    elif session.get('video_on'):
        session.pop('video_on', None)
        print('Video is off')
        flash('Video is off')
        return redirect(url_for('picam'))


# The function below is executed when someone requests a URL with a move direction
@app.route("/<direction>")
def move(direction):
    # Choose the direction of the request
    if direction == 'left':
        # Increment the angle by 10 degrees
        na = pins[23]['angle'] + 10
        # Verify that the new angle is not too great
        if int(na) <= 180:
            # Change the angle of the servo
            servoPan.set_servo(23, angleMap(na))
            # Store the new angle in the pins dictionary
            pins[23]['angle'] = na
        return str(na) + ' ' + str(angleMap(na))
    elif direction == 'right':
        na = pins[23]['angle'] - 10
        if na >= 0:
            servoPan.set_servo(23, angleMap(na))
            pins[23]['angle'] = na
        return str(na) + ' ' + str(angleMap(na))
    elif direction == 'down':
        na = pins[22]['angle'] + 10
        if na <= 180:
            servoTilt.set_servo(22, angleMap(na))
            pins[22]['angle'] = na
        return str(na) + ' ' + str(angleMap(na))
    elif direction == 'up':
        na = pins[22]['angle'] - 10
        if na >= 0:
            servoTilt.set_servo(22, angleMap(na))
            pins[22]['angle'] = na
        return str(na) + ' ' + str(angleMap(na))


# Function to manually set a motor to a specific pluse width
@app.route("/<motor>/<pulsewidth>")
def manual(motor, pulsewidth):
    if motor == "pan":
        servoPan.set_servo(23, int(pulsewidth))
    elif motor == "tilt":
        servoTilt.set_servo(22, int(pulsewidth))
    return "Moved"


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if session.get('logged_in'):
        return redirect(url_for('picam'))
    elif request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('picam'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    GPIO.output(laser, 0)
    session.pop('laser_on', None)
    session.pop('video_on', None)
    session.pop('logged_in', None)
    flash('Logged out')
    return redirect(url_for('login'))


@app.route('/shutdown')
def shutdown():
    GPIO.output(laser, 0)
    session.pop('laser_on', None)
    session.pop('video_on', None)
    session.pop('logged_in', None)
    shutdown_server()
    return 'Server shutting down...'

# Clean everything up when the app exits
atexit.register(cleanup)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
