import os
import subprocess
import sys
import re
from time import sleep


#################################################################
# Define global constants to use for menu display and navigation
#################################################################
refresh = 1
ON = "+"
OFF = "-"

class PiServicesMenu:

  def __init__(self, lcd):
    self.lcd = lcd

    # draw initial menu state
    self.drawMenu()


  def drawMenu(self):
    while True:
      status = subprocess.check_output(['lpstat', '-p'])
      #pstatus = status[:16] + '\n' + status[16:]
      #pstatus = lstatus[1][:16] + '\n' + '\n'
      if len(status) > 16:
        pstatus = status[:16] + '\n' + '\n'
      else:
        pstatus = status
      lcd.clear()
      lcd.message(pstatus)

      sleep(1)
      i = 0
      while len(status) > 16 and i < len(status)-16:
        tpstatus = status[i:i+16] + '\n' + '\n'
        i += 1
        newstatus = subprocess.check_output(['lpstat', '-p'])
        if newstatus != status:
          break
        lcd.clear()
        lcd.message(tpstatus)
        sleep(0.2)



if __name__ == '__main__':
  sys.path.append(os.path.abspath('./Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate'))
  import Adafruit_CharLCDPlate
  lcd = Adafruit_CharLCDPlate.Adafruit_CharLCDPlate(busnum = 0)

  menu = PiServicesMenu(lcd)


