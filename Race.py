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

def setEngineSpeed(percent, pwm):
    if percent < 0:
        percent = 0
    if percent > 1:
        percent = 1
    newSpeed = int(1000000 * percent + 1000000)
    pwm.duty_cycle = newSpeed

def turn(percent, pwm):
    if percent < -1:
        percent = -1
    if percent > 1:
        percent = 1
    if percent < 0:
        pwm.duty_cycle = int(1450000 + 500000 * percent)
    else:
        pwm.duty_cycle = int(500000 * percent + 1450000)

# Set the speed to be a discounted rate of the maxSpeed
def getNewSpeed(turnPercent):
    speed = 0.25 - (turnPercent * 1.8*0.25)
    if(speed < 0.17):
        speed = 0.17
    return speed


# Setup and export pwm0 and pwm1
pwm0 = PWM(0)
pwm1 = PWM(1)
pwm0.export()
pwm1.export()

pwm0.period = 20000000
pwm1.period = 20000000

setEngineSpeed(0, pwm1)
turn(0, pwm0)

pwm0.enable = True
pwm1.enable = True

time.sleep(5)

# START OF COMPUTER VISION
res = (640,480)
b, a = butter(3, 0.007)
camera = PiCamera()
camera.sensor_mode = 6
camera.resolution = res
camera.framerate = 60
rawCapture = PiYUVArray(camera, size=res)
stream = camera.capture_continuous(rawCapture, format="yuv", use_video_port=True)
whiteCenterLine = 0 # Know where the center is


def func():
    turning = 'n' # Indicate which direction it is turning
    output = 0 # result of the PID
    oldNumsPeaks = 1
    finLineCounter = 0
    pid = PID(0.1, 0, 0.1, setpoint=0) # PID used to follow the line
    pid.sample_time = 0.016
    pid.output_limits = (-1, 1)
    pid.proportional_on_measurement = True
    start_time = time.time()
    for f in stream:
        L = f.array[440, :, 0]
        rawCapture.truncate(0)
        Lf = filtfilt(b, a, L)

        # Find peaks which are higher than 0.5
        p = find_peaks(Lf, height=128)
        num_peaks = len(p[0])
        if num_peaks == 1:
            whiteCenterLine = p[0][0]
        elif num_peaks >= 2:
            whiteCenterLine = (p[0][0] + p[0][len(p)-1]) / 2
            finLineCounter += 1
        elif (num_peaks == 0):
            pass # REMEMBER LAST TURN
        
        if num_peaks == 0:
            # print("I AM NOT SEEING PEAKS")
            if turning == 'l':
                output = 1
            elif turning == 'r':
                output = -1
        else:
            percentOff = (whiteCenterLine - 320) / 240
            #print("percentOff")
            #print(percentOff)
            if percentOff >= 0.5:
                setEngineSpeed(0.16,pwm1)
            output = pid(percentOff) # Get the output of the PID as a percent
            #print("output")
            #print(output)
            if whiteCenterLine < 320:
                turning = 'l'
            else:
                turning = 'r'

        newSpeed = getNewSpeed(abs(output))

        if newSpeed <= 0.25:
            setEngineSpeed(newSpeed, pwm1)
        else:
            setEngineSpeed(0.25, pwm1)
        #print("Output: ", output)
        turn(output, pwm0) # Turn the car
        oldNumPeaks = num_peaks

        if not running.value:
            running.value = True
            break
        if time.time() - start_time < 4:
            pass
        elif finLineCounter >= 2:
            time.sleep(0.5) # Give time to cross the finish line (May need to be changed with testing)
            break
        if finLineCounter == 1:
            if time.time() - start_time > 5:
                time.sleep(0.70)
                break
            else:
                finLineCounter -= 1
            
    # Stop the motor
    setEngineSpeed(0, pwm1)
    # Reposition the servo to 0
    turn(0, pwm0)
    time.sleep(.1)
    stream.close()
    rawCapture.close()
    camera.close()
    pwm0.enable = False
    pwm1.enable = False
t = threading.Thread(target=func)
t.start()