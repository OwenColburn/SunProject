# Main project file for Raspberry Pi Sun Project
# Code written by Owen Colburn, 2024

import I2C_LCD_driver  # I2C_LCD_driver.py must be in the same folder for this to work, otherwise must specify path
import os
import datetime
import pandas as pd
from gpiozero import Servo, Device
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

MATHEMATICA_FILE_PATH = "/PATH/TO/sunCode-1.nb"  # Mathematica file location. CHANGE WITH CORRECT FILE PATH
SUN_DATA_FILE_PATH = "/PATH/TO/sunData.ods"      # Sun data sheet file location. CHANGE WITH CORRECT FILE PATH

def action(row_number, sun_data, mylcd, servo):
  mylcd.lcd_display_string("Data collected! ",1,0)
  sleep(1)
  mylcd.lcd_display_string("Current Azimuth:",1,0)

  azimuth_degrees = sun_data.iloc[row_number,0]
  servo_value = azimuth_degrees if (azimuth_degrees < 180) else azimuth_degrees - 180  # Adjust the value passed to the servo if the angle is too much

  # Rotate the servo
  deg_to_ms(servo_value, servo)

  # Print the information to the LCD
  mylcd.lcd_display_string("%d degrees " % azimuth_degrees, 2, 0)

# Convert a degree to a number of ms to rotate the servo
def deg_to_ms(deg, servo):
  # If the degree is greater than 90, then subtract 180 and divide by 90
  # else, servo.value is just -deg/90
  # The servo only takes values between -1 and 1, so this calculates the value that the servo will receive.
  servo.value = -(deg - 180)/90 if deg > 90 else -deg/90
  sleep(1)  # Give the servo time to rotate

def main():
  #Initialize the LCD
  mylcd = I2C_LCD_driver.lcd()

  # Set the pin factory to PiGPIO
  Device.pin_factory = PiGPIOFactory()

  # Initialize the Servo on pin 17. Notice not being initialized on GPIO 11
  servo = Servo(17, min_pulse_width=0.5/1000, max_pulse_width=2.25/1000)  # values of min and max pulse width were experimentally found to give best results. Might change based on the servo used

  # Calculate the number of minutes passed since midnight
  hours_as_minutes = datetime.datetime.now().hour * 60
  minutes_elapsed = datetime.datetime.now().minute + hours_as_minutes

  # Would usually have to check if we are at a 15 minute interval, but this is handled by the cron-job

  row_number = minutes_elapsed // 15  # Integer division

  if (row_number == 0):  # i.e. If it's midnight
    mylcd.lcd_display_string("Getting data... ", 1, 0)

    # Get new data for the day
    os.system('wolframscript -file {}'.format(MATHEMATICA_FILE_PATH))  # Remember to change the file location based on your system
  
  # Read in sun data from sunData.ods using pandas
  sun_data = pd.read_excel(f"{SUN_DATA_SHEET_PATH}", header=None)

  # Run the action method to print to LCD and rotate Servo
  action(row_number=row_number, sun_data=sun_data, mylcd=mylcd, servo=servo)

  # Remove the servo and lcd from software, just in case
  servo = None
  mylcd = None

# Only run this file if this file specifically was called
if __name__ == "__main__":
  main()
