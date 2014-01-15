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

    return services


  def toggleService(self, svcIdx):
    action = " start"
    if self.services[svcIdx][0] == ON:
      action = " stop"
    try:
      serviceOut = subprocess.check_output(["service", self.services[svcIdx][1], action])
      self.lcd.clear()
      self.lcd.message(serviceOut)
      if self.services[svcIdx][0] == OFF:
        self.services[svcIdx][0] = ON
      elif self.services[svcIdx][0] == ON:
        self.services[svcIdx][0] = OFF
    except subprocess.CalledProcessError as e:
      self.lcd.clear()
      self.lcd.message(e)
      print e
    sleep(2)


  def runMenu(self):
    buttons = (lcd.SELECT,
               lcd.LEFT,
               lcd.UP,
               lcd.DOWN,
               lcd.RIGHT)

    # Keep toggle state status outside of loop that way the SELECT button can know if a new state needs
    # to be toggled after a UP/DOWN button has been pressed within a service status screen 
    toggleState = False

    # buttons aren't event/trigger driven, we need to constantly poll in a loop for button presses
    while True:
      # only trigger display change if button is pressed
      btnPress = False

      # Select button applies new service state (on/off) after having been toggled
      if lcd.buttonPressed(lcd.SELECT):
        btnPress = True
        if toggleState:
          self.toggleService(self.menuIdx)
          toggleState = False

      if lcd.buttonPressed(lcd.LEFT): 
        btnPress = True
        toggleState = False
        self.menuLvl -= 1
        if self.menuLvl < 0:
          self.menuLvl = 0

      if lcd.buttonPressed(lcd.RIGHT): 
        btnPress = True
        self.menuLvl += 1
        if self.menuLvl > 2:
          self.menuLvl = 2

      # UP/DOWN buttons navigate the services list, as well as toggle on/off state for the selected service.
      # Service states always show "on" state as first line and "off" state on second line.
      # There is no circular scrolling through this list, pressing the UP button when the "on" state is
      # selected does nothing, just as pressing the DOWN button when "off" state is selected does nothing.
      # Only set the service's selected on/off state when it differs from its current state.

      if lcd.buttonPressed(lcd.UP):
        btnPress = True
        if self.menuLvl == 1:
          self.menuIdx -= 1
          if self.menuIdx < 0:
            self.menuIdx = 0
        elif self.menuLvl == 2:
          if toggleState:
            toggleState = False
          elif self.services[self.menuIdx][0] == OFF:
            toggleState = True
          
      if lcd.buttonPressed(lcd.DOWN):
        btnPress = True
        if self.menuLvl == 1:
          self.menuIdx += 1
          if self.menuIdx > len(self.services) - 1:
            self.menuIdx = len(self.services) - 1
        elif self.menuLvl == 2:
          if toggleState:
            toggleState = False
          elif self.services[self.menuIdx][0] == ON:
            toggleState = True

      if btnPress:
        self.drawMenu(self.menuLvl, self.menuIdx, toggleState)
        sleep(0.5)
  
  def drawMenu(self, lvl, idx, toggle = False):
    self.lcd.clear()
    if lvl == 0:
      self.lcd.message("System services >")
    elif lvl == 1:
      self.lcd.message(self.services[idx][1])
    elif lvl == 2:
      if toggle:
        msg = " [on]\n= off ="
        if self.services[idx][0] == ON:
          msg = "= on =\n [off]"
        self.lcd.message(msg)
      else:
        msg = "  on\n=[off]="
        if self.services[idx][0] == ON:
          msg = "=[on]=\n  off"
        self.lcd.message(msg)



if __name__ == '__main__':
  sys.path.append(os.path.abspath('./Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate'))
  import Adafruit_CharLCDPlate
  lcd = Adafruit_CharLCDPlate.Adafruit_CharLCDPlate(busnum = 1)
  lcd.backlight(lcd.RED)

  if len(sys.argv) > 1 and sys.argv[1] == 'off':
    lcd.backlight(lcd.OFF)
  else:
    menu = PiServicesMenu(lcd)
    menu.runMenu()
    del menu

  if lcd:
    del lcd
  
