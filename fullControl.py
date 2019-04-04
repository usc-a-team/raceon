from picamera.array import PiYUVArray, PiRGBArray
from picamera import PiCamera
from scipy.signal import find_peaks, butter, filtfilt
from simple_pid import PID
import time
import matplotlib.pyplot as plt
import skimage as ski
import numpy as np

# Takes in a percent and a pwm, sets the speed according to the percent
def setEngineSpeed(percent, pwm):
    # If the percent is less than 0, set to 0
    if percent < 0:
        percent = 0
	# If the percent is greater than 1, set to 1
    if percent > 1:
        percent = 1
	# Calculate the speed to set the motor
    speed = int(1000000 * percent + 1000000)
    #print("set engine speed ", speed)
	# Set the duty_cylce to the speed
    pwm.duty_cycle = speed

# Takes in a percent and a pwm, turns to the right according to the percent
def turnRight(percent, pwm):
	# If the percent is less than 0, set to 0
    if percent < 0:
        percent = 0
	# If the percent is greater than 1, set to 1
    if percent > 1:
        percent = 1
	# Calculate the direction to set the servo
    value = int(1500000 - 500000 * percent)
    #print("turn right speed: ", value)
	# Set the duty_cylce to the value
    pwm.duty_cycle = value

# Takes in a percent and a pwm, turns to the left according to the percent
def turnLeft(percent, pwm):
	# If the percent is less than 0, set to 0
    if percent < 0:
        percent = 0
	# If the percent is greater than 1, set to 1
    if percent > 1:
        percent = 1
	# Calculate the direction to set the servo
    value = int(500000 * percent + 1500000)
    #print("turn left speed: ", value)
	# Set the duty_cylce to the value
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
    
# Import the pwm and time
from pwm import PWM
import time

# Setup and export pwm0 and pwm1
pwm0 = PWM(0)
pwm1 = PWM(1)
pwm0.export()
pwm1.export()

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
b, a = butter(3, 0.02)


camera = PiCamera()


# Check the link below for the combinations between mode and resolution
# https://picamera.readthedocs.io/en/release-1.13/fov.html#sensor-modes
camera.sensor_mode = 7
camera.resolution = res
camera.framerate = 60

# Initialize the buffer and start capturing
rawCapture = PiYUVArray(camera, size=res)
stream = camera.capture_continuous(rawCapture, format="yuv", use_video_port=True)

# Measure the time needed to process 300 images to estimate the FPS
N = 1000
k = 0
t = time.time()

pid = PID(.8, 0.1, 0.05, setpoint=320)
pid.sample_time = 0.05
setEngineSpeed(0.14, pwm1)
whiteCenterLine = (0,0)
for f in stream:
    # Get the intensity component of the image (a trick to get black and white images)
    I = f.array[:, :, 0]
    
    # Reset the buffer for the next image
    rawCapture.truncate(0)
    
    # Select a horizontal line in the middle of the image
    L = I[440, :]

    # Smooth the transitions so we can detect the peaks 
    Lf = filtfilt(b, a, L)

    # Find peaks which are higher than 0.5
    p = find_peaks(Lf, height=128)
    num_peaks = len(p[0])
    for x in range(num_peaks):
        p[0][x] -=25;
    if num_peaks == 1:
        whiteCenterLine = ((p[0][0] - 75, p[0][0] + 75))
        whiteCenterLine_frame = k
    elif num_peaks > 2:
        whiteCenterLine = ((p[0][0] + p[0][1] / 2) - 75, (p[0][0] + p[0][1] / 2) + 75)
        whiteCenterLine_frame = k
    elif (num_peaks == 2):
        #print(p)
        whiteCenterLine = ((p[0][0] + p[0][1] / 2) - 75, (p[0][0] + p[0][1] / 2) + 75) # Should be (245, 395)
        whiteCenterLine_frame = k
    elif (num_peaks == 0):
        pass # REMEMBER LAST TURN
    # Print peaks
    #### print(p)
    
    # Here we should steer and then update to the next frame.
    if num_peaks > 2:
        print("num peaks ", num_peaks)
    if num_peaks == 0:
          pass
    else:
        output = pid(whiteCenterLine[0] + 75)
        turn(output, pwm0)
    
    
    ##current_value = controlled_system.update(output)
          
    # Increment the number of processed frames
    k += 1
    if k > N:
        break

# Stop the motor
setEngineSpeed(0, pwm1)
time.sleep(.1)

#time_elapsed = time.time() - t
#print("Elapsed {:0.2f} seconds, estimated FPS {:0.2f}".format(time_elapsed, N / time_elapsed))

stream.close()
rawCapture.close()
camera.close()


# Disable both pwms
pwm0.enable = False
pwm1.enable = False

# Unexport both pwms
pwm0.unexport()
pwm1.unexport()
quit()
