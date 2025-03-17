import RPi.GPIO as GPIO
import time

# GPIO setup
servo_pin = 18  # Replace with the GPIO pin you connected the servo's signal wire to
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# PWM setup
pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz frequency
pwm.start(0)  # Start PWM with a duty cycle of 0%

def set_angle(angle):
    duty = 2 + (angle / 18)  # Convert angle to duty cycle (adjust 2 and 12 for your servo)
    GPIO.output(servo_pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)  # Give the servo time to move
    GPIO.output(servo_pin, False)
    pwm.ChangeDutyCycle(0)

try:
    while True:
        angle = float(input("Enter angle (0 to 180): "))  # Get angle input
        if 0 <= angle <= 180:
            set_angle(angle)
        else:
            print("Please enter a value between 0 and 180.")
except KeyboardInterrupt:
    print("Program stopped.")
finally:
    pwm.stop()
    GPIO.cleanup()
