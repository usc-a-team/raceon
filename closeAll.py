from picamera.array import PiYUVArray, PiRGBArray
from picamera import PiCamera
from scipy.signal import find_peaks, butter, filtfilt
from simple_pid import PID
import time
import matplotlib.pyplot as plt
import skimage as ski
import numpy as np
    
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
setEngineSpeed(0, pwm0)
turnRight(0, pwm1)

# Enable the pwms
pwm0.enable = True
pwm1.enable = True

# Give some time to start up
time.sleep(5)

stream.close()
rawCapture.close()
camera.close()
setEngineSpeed(0, pwm0)
time.sleep(.1)

# Disable both pwms
pwm0.enable = False
pwm1.enable = False

# Unexport both pwms
pwm0.unexport()
pwm1.unexport()
quit()
