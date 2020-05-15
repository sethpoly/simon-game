import RPi.GPIO as GPIO
import random
import time
import os
import threading

class wrong_button_exception(Exception):
    pass

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Set up the led outputs
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)
GPIO.setup(23, GPIO.OUT)

# Set up button input
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP) # was gpio4
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# List to hold the current simon pattern
pattern_list = {}

# List of possible simon outputs
possible_outputs = {17: 'y', 27: 'g', 22: 'b', 23: 'r'}

# Button corresponding color pins
button_ids = {'y': 2, 'g': 3, 'b': 26, 'r': 14}

# Speed inbetween flashing lights
gamespeed = .5

# Duration light is shown
lightduration = .65

# The next button to be pressed in the pattern
current_button = 0

#Checks if game is over
gameover = False

def button_handler(channel):
    try: 
        if current_button != channel:
            raise wrong_button_exception

    except wrong_button_exception:
        removeWrongButtonListeners()
        endGame()
        print("Wrong button pressed")
        

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

def addWrongButtonListeners():
    GPIO.add_event_detect(2, GPIO.RISING, callback=button_handler, bouncetime=200)
    GPIO.add_event_detect(3, GPIO.RISING, callback=button_handler, bouncetime=200)
    GPIO.add_event_detect(26, GPIO.RISING, callback=button_handler, bouncetime=200)
    GPIO.add_event_detect(14, GPIO.RISING, callback=button_handler, bouncetime=200)
    
def removeWrongButtonListeners():
    GPIO.remove_event_detect(2)
    GPIO.remove_event_detect(3)
    GPIO.remove_event_detect(26)
    GPIO.remove_event_detect(14)
    

# Retrieve the user input
def getUserInput():
    for key in pattern_list.keys():
        for led in pattern_list[key]:
            print("START")
            print(button_ids[pattern_list[key][led]])
            button = button_ids[pattern_list[key][led]]
            global current_button  # Reference the next button to be pressed
            current_button = button
                        
            # Add listeners for the wrong button press
            addWrongButtonListeners()

            # Remove evebt detect for next button to be pressed bc it conflicts with wait_for_edge
            GPIO.remove_event_detect(button)
            
            channel = GPIO.wait_for_edge(button, GPIO.RISING, timeout=3000)
            if channel is None:
                return False
            else:
                time.sleep(.3)
                if GPIO.input(button) == GPIO.LOW and not gameover:
                    print('Correct')

            removeWrongButtonListeners()
    return True

# Illuminates the LED then calls func to play a sound
# @param led is the pin, color is the name of the color
def ledLight(led, color):    
    GPIO.output(led, 1)
    
    # Start new thread to synchronize beep with led 
    t = threading.Thread(target = ledSound, args = (led, color))
    t.daemon = True
    t.start()
    
    time.sleep(lightduration)
    GPIO.output(led, 0)
    time.sleep(gamespeed)
    
# Plays a short sound for each color
def ledSound(led, color):
    if(color == 'y'):
        os.system("play -n synth %s sin %s" % (lightduration, 800)) # dur, freq
    elif(color == 'g'):
        os.system("play -n synth %s sin %s" % (lightduration, 1100)) # dur, freq
    elif(color == 'b'):
        os.system("play -n synth %s sin %s" % (lightduration, 500)) # dur, freq
    elif(color == 'r'):
        os.system("play -n synth %s sin %s" % (lightduration, 200)) # dur, freq

        
def prepareGame():
    # Low lights if HIGH
    turnOffLEDS()
    
    # Light show
    t = threading.Thread(target = strobeLEDS, args = ())
    t.daemon = True
    t.start()
    
    # Happy beeps
    playHappyBeeps()
    
    time.sleep(1)
    
# Sad beeps
def playSadBeeps():
    os.system("play -n synth %s sin %s" % (.2, 300)) # dur, freq
    os.system("play -n synth %s sin %s" % (.2, 200)) # dur, freq
    os.system("play -n synth %s sin %s" % (.5, 100)) # dur, freq

# Happy beeps
def playHappyBeeps():
    os.system("play -n synth %s sin %s" % (.2, 100)) # dur, freq  
    os.system("play -n synth %s sin %s" % (.2, 200)) # dur, freq
    os.system("play -n synth %s sin %s" % (.5, 300)) # dur, freq

# Show score, sad beeping, flash lights
def endGame():
    global gameover
    gameover = True
    
    score = len(pattern_list) - 1 # the users total score
    
    # Light show
    t = threading.Thread(target = strobeLEDS, args = ())
    t.daemon = True
    t.start()
    
    # Sad beeping tune
    playSadBeeps()
    
    # Display losing msg and score
    print("INCORRECT - YOU LOSE")
    print("Your score: %s" % (score))
    GPIO.cleanup()
   

def startGame():
    global gameover
    prepareGame()
    while True:
        pin, color = random_output() # Get random next light patern
        pattern_list.setdefault(len(pattern_list) - 1, {})[pin] = color # add the next pattern to the list

        displayPattern() # Display the full pattern for user to memorize
        if not getUserInput(): # Await user input
            if not gameover:
                endGame()
            return
            

# Start the game
startGame()

      


    
    
    
    
    
    
    
    
    
