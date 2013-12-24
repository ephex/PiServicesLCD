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
    self.services = self.getServices()
    self.menuIdx = 0
    self.menuLvl = 0

    # draw initial menu state
    self.drawMenu(self.menuLvl, self.menuIdx)

  def getServices(self):
    services = []
    try:
      serviceOut = subprocess.check_output(["service", "--status-all"])
      serviceLines = serviceOut.splitlines()
      for line in serviceLines:
        expr = re.compile(r"\s+\[\s{1}([\+-\?])\s\]\s+(.*)")
        matches = expr.match(line)

        if matches and len(matches.groups()) == 2:
          services.append([matches.group(1), matches.group(2)])
    except subprocess.CalledProcessError as e:
      print e

    print services
    return services


  def runMenu(self):
    buttons = (lcd.SELECT,
               lcd.LEFT,
               lcd.UP,
               lcd.DOWN,
               lcd.RIGHT)
    # buttons aren't event/trigger driven, we need to constantly poll in a loop for button presses
    while True:
      # only trigger display change if button is pressed
      btnPress = False

      if lcd.buttonPressed(lcd.SELECT):
        btnPress = True
        self.menuLvl -= 1
        if self.menuLvl < 0:
          self.menuLvl = 0

      if lcd.buttonPressed(lcd.LEFT): 
        btnPress = True
        self.menuLvl -= 1
        if self.menuLvl < 0:
          self.menuLvl = 0

      if lcd.buttonPressed(lcd.RIGHT): 
        btnPress = True
        self.menuLvl += 1
        if self.menuLvl > 2:
          self.menuLvl = 2

      if lcd.buttonPressed(lcd.UP):
        btnPress = True
        if self.menuLvl == 1:
          self.menuIdx -= 1
          if self.menuIdx < 0:
            self.menuIdx = 0

      if lcd.buttonPressed(lcd.DOWN):
        btnPress = True
        if self.menuLvl == 1:
          self.menuIdx += 1
          if self.menuIdx > len(self.services) - 1:
            self.menuIdx = len(self.services) - 1

      if btnPress:
        self.drawMenu(self.menuLvl, self.menuIdx)
        sleep(0.5)
  
  def drawMenu(self, lvl, idx):
    self.lcd.clear()
    if lvl == 0:
      self.lcd.message("System services >")
    elif lvl == 1:
      self.lcd.message(self.services[idx][1])
    elif lvl == 2:
      msg = "on\n[off]"
      if self.services[idx][0] == ON:
        msg = "[on]\noff"
      self.lcd.message(msg)


if __name__ == '__main__':
  sys.path.append(os.path.abspath('./Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate'))
  import Adafruit_CharLCDPlate
  lcd = Adafruit_CharLCDPlate.Adafruit_CharLCDPlate(busnum = 1)

  menu = PiServicesMenu(lcd)
  menu.runMenu()
