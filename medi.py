import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from datetime import datetime, time as dt_time

# Set the GPIO mode
GPIO.setmode(GPIO.BOARD)

# Define the motor driver pins for the stepper motor
motor_pins = [13, 11, 15, 12]

# Set the motor pins as output
for pin in motor_pins:
    GPIO.setup(pin, GPIO.OUT)

# Define the servo motor pin
servo_pin = 16

# Create an instance of the RFID reader
reader = SimpleMFRC522()

# Define the stepper motor sequence
seq = [
    [1, 0, 0, 1],  # Step 1
    [1, 0, 0, 0],  # Step 2
    [1, 1, 0, 0],  # Step 3
    [0, 1, 0, 0],  # Step 4
    [0, 1, 1, 0],  # Step 5
    [0, 0, 1, 0],  # Step 6
    [0, 0, 1, 1],  # Step 7
    [0, 0, 0, 1]   # Step 8
]

try:
    while True:
        current_time = datetime.now().time()

        # Check if the current time is within the desired time range
        start_time = dt_time(14, 38)  # Start time: 2:38 PM
        end_time = dt_time(14, 45)    # End time: 2:45 PM

        if start_time <= current_time <= end_time:
            # Wait for an RFID tag to be detected
            print("Hold a tag near the reader")
            id, text = reader.read()

            # If a tag is detected, activate the stepper motor and servo motor
            if id is not None:
                print("Tag detected")

                # Function to move the stepper motor for 60 degrees clockwise
                def move_stepper_motor_clockwise(delay):
                    steps = 0
                    while steps < 100:  # Adjust steps for 60 degrees rotation
                        for halfstep in range(8):
                            for pin in range(4):
                                GPIO.output(motor_pins[pin], seq[halfstep][pin])
                            time.sleep(delay)
                            steps += 1

                # Function to move the stepper motor for 60 degrees counterclockwise
                def move_stepper_motor_counterclockwise(delay):
                    steps = 0
                    while steps < 100:  # Adjust steps for 60 degrees rotation
                        for halfstep in range(7, -1, -1):
                            for pin in range(4):
                                GPIO.output(motor_pins[pin], seq[halfstep][pin])
                            time.sleep(delay)
                            steps += 1

                # Code for controlling the servo motor
                GPIO.setup(servo_pin, GPIO.OUT)
                pwm = GPIO.PWM(servo_pin, 50)  # 50 Hz frequency
                pwm.start(0)

                # Rotate the stepper motor 60 degrees clockwise
                move_stepper_motor_clockwise(0.01)

                # Rotate the servo motor 120 degrees clockwise
                duty_cycle = 2 + (120 / 18)  # Calculate duty cycle for 120 degrees
                GPIO.output(servo_pin, True)
                pwm.ChangeDutyCycle(duty_cycle)
                time.sleep(1)
                GPIO.output(servo_pin, False)
                pwm.ChangeDutyCycle(0)

                # Rotate the servo motor 120 degrees counterclockwise
                duty_cycle = 2 + (0 / 18)  # Calculate duty cycle for 0 degrees
                GPIO.output(servo_pin, True)
                pwm.ChangeDutyCycle(duty_cycle)
                time.sleep(1)
                GPIO.output(servo_pin, False)
                pwm.ChangeDutyCycle(0)

                # Rotate the stepper motor 60 degrees counterclockwise
                move_stepper_motor_counterclockwise(0.01)

                pwm.stop()

        # Delay between checking the time
        time.sleep(60)  # Check every minute

except KeyboardInterrupt:
    # Stop the motors and cleanup GPIO pins on keyboard interrupt
    GPIO.output(motor_pins, 0)
    GPIO.cleanup()
