from picamera.array import PiYUVArray, PiRGBArray
from picamera import PiCamera
from scipy.signal import find_peaks, butter, filtfilt
from simple_pid import PID
from pwm import PWM
import ipywidgets as ipw
import time
import matplotlib.pyplot as plt
import skimage as ski
import numpy as np
import time
import threading

# Takes in a percent and a pwm, sets the speed according to the percent
def setEngineSpeed(percent, pwm):
    if percent < 0:
        percent = 0
    if percent > 1:
        percent = 1
    newSpeed = int(1000000 * percent + 1000000)
    pwm.duty_cycle = newSpeed

# Takes in a percent and a pwm, turns to the right according to the percent
def turnRight(percent, pwm):
    if percent < 0:
        percent = 0
    if percent > 1:
        percent = 1
    value = int(1450000 - 950000 * percent)
    pwm.duty_cycle = value

# Takes in a percent and a pwm, turns to the left according to the percent
def turnLeft(percent, pwm):
    if percent < 0:
        percent = 0
    if percent > 1:
        percent = 1
    value = int(440000 * percent + 1450000)
    pwm.duty_cycle = value

def turn(percent, pwm):
    if percent < -1:
        percent = -1
    if percent > 1:
        percent = 1
    if percent < 0:
        turnRight(-1 * percent, pwm)
    else:
        turnLeft(percent, pwm)
        
# Set the speed to be a discounted rate of the maxSpeed
def getNewSpeed(turnPercent, maxSpeed, minSpeed):
    speed = maxSpeed - (turnPercent * maxSpeed)
    if(speed < minSpeed):
        speed = minSpeed
    return speed
pwm0 = PWM(0)
pwm1 = PWM(1)
pwm0.export()
pwm1.export()


# -------------------------------------------------------------------------------------------------
# END OF FUNCTIONS 

# Set the periods to 20ms
pwm0.period = 20000000
pwm1.period = 20000000

# Set the duty_cycle of the motor to 1ms and servo to 1.5ms
setEngineSpeed(0, pwm1)
turnRight(0, pwm0)

# Enable the pwms
pwm0.enable = True
pwm1.enable = True

# Give some time to start up
time.sleep(5)

# START OF COMPUTER VISION
res = (640,480)
b, a = butter(3, 0.007)
camera = PiCamera()
camera.sensor_mode = 7
camera.resolution = res
camera.framerate = 60

# Initialize the buffer and start capturing
rawCapture = PiYUVArray(camera, size=res)
stream = camera.capture_continuous(rawCapture, format="yuv", use_video_port=True)

whiteCenterLine = 0 # Know where the center is
turning = 'n' # Indicate which direction it is turning
output = 0 # result of the PID
finLineCounter = 0 # Used to count the number of times the car passes the finish line
oldNumsPeaks = 1
pid = PID(0.3, 0.1, 0.2, setpoint=0) # PID used to follow the line
pid.sample_time = 0.05

for f in stream:
    I = f.array[:, :, 0]
    rawCapture.truncate(0)
    L = I[440, :]
    Lf = filtfilt(b, a, L)

    # Find peaks which are higher than 0.5
    p = find_peaks(Lf, height=128)
    num_peaks = len(p[0])
    if num_peaks == 1:
        whiteCenterLine = p[0][0]
    elif num_peaks >= 2:
        whiteCenterLine = (p[0][0] + p[0][len(p)-1]) / 2
        # finLineCounter += 1

    if num_peaks == 0:
        if turning == 'l':
            output = 1
        elif turning == 'r':
            output = -1
    else:
        # Check that the line is not one of the edge lines. Continue on the same path if it is
        if turning == 'l' and whiteCenterLine - 320 > 150 and oldNumPeaks == 0 and False:
            pass
        elif turning == 'r' and whiteCenterLine < 150 and oldNumPeaks == 0  and False:
            pass
        else:
            # Get how far the car is off as a percent
            percentOff = (whiteCenterLine - 320) / 320
            output = pid(percentOff) # Get the output of the PID as a percent
            if whiteCenterLine < 320:
                turning = 'l'
            else:
                turning = 'r'

    newSpeed = getNewSpeed(abs(output), .25, .17)
    setEngineSpeed(newSpeed, pwm1)

    turn(output, pwm0) # Turn the car
    oldNumPeaks = num_peaks

   # if finLineCounter >= 1:
    #    time.sleep(0.5) # Give time to cross the finish line (May need to be changed with testing)
    #    break
# Stop the motor
setEngineSpeed(0, pwm1)
# Reposition the servo to 0
turnRight(0, pwm0)
time.sleep(.1)

# Close the camera and the stream
stream.close()
rawCapture.close()
camera.close()
# Disable both pwms
pwm0.enable = False
pwm1.enable = False