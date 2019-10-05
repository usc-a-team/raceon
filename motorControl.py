from pwm import PWM
import time
pwm0 = PWM(0)
pwm0.export()
pwm0.period = 20000000
pwm0.duty_cycle = 1000000
pwm0.enable = True
time.sleep(5)
pwm0.duty_cycle = 1100000
time.sleep(10)
pwm0.duty_cycle = 1200000
time.sleep(1)
pwm0.duty_cycle = 1300000
time.sleep(1)
pwm0.duty_cycle = 1000000
time.sleep(0.5)
pwm0.enable = False
pwm0.unexport()
quit()
