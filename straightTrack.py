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
	# Set the duty_cylce to the value
	pwm.duty_cycle = value

# Import the pwm and time
from pwm import PWM
import time

# Setup and export pwm0 and pwm1
pwm0 = PWM(1)
pwm1 = PWM(0)
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

# Perform a serpentine motion (5 seconds)
# Run motor at 25% and change direction every 1 seconds
setEngineSpeed(.25, pwm0)
time.sleep(2.5)

# Stop the motor
setEngineSpeed(0, pwm0)
time.sleep(.1)

# Disable both pwms
pwm0.enable = False
pwm1.enable = False

# Unexport both pwms
pwm0.unexport()
pwm1.unexport()
quit()
