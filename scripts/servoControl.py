from pwm import PWM
import time
pwm1 = PWM(1)
pwm1.export()
pwm1.period = 20000000
pwm1.duty_cycle = 1500000
pwm1.enable = True
time.sleep(5)
pwm1.duty_cycle = 2000000
time.sleep(2)
pwm1.duty_cycle = 1000000
time.sleep(2)
pwm1.duty_cycle = 1500000
time.sleep(0.5)
pwm1.enable = False
pwm1.unexport()
quit()
