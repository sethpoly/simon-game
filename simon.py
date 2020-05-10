import RPi.GPIO as GPIO
import random
import time
import os
import threading 

# Set ip GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up the led IOS
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

# List to hold the current simon pattern
pattern_list = {}

# List of possible simon outputs
possible_outputs = {17: 'y', 27: 'g', 22: 'b', 23: 'r'}

# Clear leds
def turnOffLEDS():
    GPIO.output(17, 0)
    GPIO.output(27, 0)
    GPIO.output(22, 0)
    GPIO.output(23, 0)
    
# Turn on all leds
def turnOnLEDS():
    GPIO.output(17, 1)
    GPIO.output(27, 1)
    GPIO.output(22, 1)
    GPIO.output(23, 1)
    
# Flash the leds
def strobeLEDS():
    turnOffLEDS()
    turnOnLEDS()
    time.sleep(.3)
    turnOffLEDS()
    time.sleep(.3)
    turnOnLEDS()
    time.sleep(.3)
    turnOffLEDS()

# Choose the random next simon output
def random_output():
    pin, color = random.choice(list(possible_outputs.items()))
    return pin, color

# Loops through each led in the pattern and lights it & plays a sound
def displayPattern():
    for key in pattern_list.keys():
        for led in pattern_list[key]:
            color = pattern_list[key][led] # Color <g>
            ledLight(led, color) # Pin is led
        
# Retrieve the user input
def getUserInput():
    for key in pattern_list.keys():
        for led in pattern_list[key]:
            user_answer = input("Type the next color (r,g,b,y): ")
            if pattern_list[key][led] != user_answer:
                return False
    return True


# Illuminates the LED and plays a sound
# @param led is the pin, color is the name of the color
def ledLight(led, color):
    dur = .8 # Length of led display
    
    print(str(led) + " on")
    GPIO.output(led, 1)
    
    # Start new thread to synchronize beep with led 
    t = threading.Thread(target = ledSound, args = (led, color, dur))
    t.daemon = True
    t.start()
    
    time.sleep(.8)
    print(str(led) + " off")
    GPIO.output(led, 0)
    time.sleep(1)
    
# Plays a short sound for each color
def ledSound(led, color, dur):
    if(color == 'y'):
        os.system("play -n synth %s sin %s" % (dur, 800)) # dur, freq
    elif(color == 'g'):
        os.system("play -n synth %s sin %s" % (dur, 1100)) # dur, freq
    elif(color == 'b'):
        os.system("play -n synth %s sin %s" % (dur, 500)) # dur, freq
    elif(color == 'r'):
        os.system("play -n synth %s sin %s" % (dur, 200)) # dur, freq
        
def endSound():
    score = len(pattern_list) - 1 # the users total score
    
    # Light show
    t = threading.Thread(target = strobeLEDS, args = ())
    t.daemon = True
    t.start()
    
    # Sad beeping tune
    os.system("play -n synth %s sin %s" % (.2, 300)) # dur, freq
    os.system("play -n synth %s sin %s" % (.2, 200)) # dur, freq
    os.system("play -n synth %s sin %s" % (.5, 100)) # dur, freq
    
    # Display losing msg and score
    print("INCORRECT - YOU LOSE")
    print("Your score: %s" % (score))


        

def startGame():
    turnOffLEDS()
    while True:
        pin, color = random_output() # add the next pattern to the list
        pattern_list.setdefault(len(pattern_list) - 1, {})[pin] = color

        displayPattern() # Display the full pattern for user to memorize
        if getUserInput() == False: # Await user input
            endSound()
            break
    
# Start the game
startGame()
      


    
    
    
    
    
    
    
    
    
