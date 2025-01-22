# Final test phase
# Pushkar Singh, 22nd January, 2025

"""
    Tasks
    - Implementing the timer is still left.
"""

from psychopy import visual, core, event, data, prefs, gui
from psychopy.event import Mouse
import random
import os
import pandas as pd
import numpy as np
prefs.hardware['audioLib'] = ['PTB']
from psychopy import sound
import tobii_research as tr

# since all checks happen only with right eye cooridinates, this variable stores the right eye data. The structure being : r.validity , r.x_cooridinate, r.y_coordinate

r = np.zeros(3)

# For Madhav
participant_id = 456
winsize = [1366,768]
experiment_name = 'Test Experiment'

# functions to store eye-tracking data

def gaze_data_callback(gaze_data):
    global trigger
    global gaze_data_buffer
    global winsize
    global r

    if len(trigger)==0:
        ev = ''
    else:
        ev = trigger
        trigger=[]
    
    # Extract the data we are interested in
    t  = gaze_data.system_time_stamp / 1000.0
    lx = gaze_data.left_eye.gaze_point.position_on_display_area[0] * winsize[0]
    ly = winsize[1] - gaze_data.left_eye.gaze_point.position_on_display_area[1] * winsize[1]
    lp = gaze_data.left_eye.pupil.diameter
    lv = gaze_data.left_eye.gaze_point.validity
    rx = gaze_data.right_eye.gaze_point.position_on_display_area[0] * winsize[0]
    ry = winsize[1] - gaze_data.right_eye.gaze_point.position_on_display_area[1] * winsize[1]
    rp = gaze_data.right_eye.pupil.diameter
    rv = gaze_data.right_eye.gaze_point.validity
        
    # Add gaze data to the buffer 
    gaze_data_buffer.append((t,lx,ly,lp,lv,rx,ry,rp,rv,ev))
    r[0] = rv
    r[1] = rx
    r[2] = ry

def write_buffer_to_file(buffer, output_path):
    # Make a copy of the buffer and clear it
    buffer_copy = buffer[:]
    buffer.clear()
    
    # Define column names
    columns = ['time', 'L_X', 'L_Y', 'L_P', 'L_V', 
               'R_X', 'R_Y', 'R_P', 'R_V', 'Event']

    # Convert buffer to DataFrame
    out = pd.DataFrame(buffer_copy, columns=columns)
    
    # Check if the file exists
    file_exists = not os.path.isfile(output_path)
    
    # Write the DataFrame to an HDF5 file
    out.to_csv(output_path, mode='a', index =False, header = file_exists)

# ROI Function
def get_area_of_interest(screen_resolution, area_of_interest, position_of_interest):
    """
    Visualizes the area of interest within the given screen resolution.
    
    Parameters:
    screen_resolution (list): A list containing the width and height of the screen resolution [width, height].
    area_of_interest (list): A list containing the width and height of the area of interest [width, height].
    position_of_interest (list): A list containing the x and y coordinates of the position of the area of interest relative to the center [x, y].
    
    Returns:
    list: A list containing the start and end coordinates of the area of interest rectangle [x_start, x_end, y_start, y_end].
    """
    screen_width, screen_height = screen_resolution
    aoi_width, aoi_height = area_of_interest
    aoi_x, aoi_y = position_of_interest
    
    # Calculate the x and y coordinates of the area of interest
    x_start = screen_width // 2 + aoi_x - aoi_width // 2
    x_end = x_start + aoi_width
    y_start = screen_height // 2 + aoi_y - aoi_height // 2
    y_end = y_start + aoi_height
    
    # Ensure the area of interest stays within the screen resolution
    x_start = max(0, min(x_start, screen_width - aoi_width))
    x_end = max(0, min(x_end, screen_width))
    y_start = max(0, min(y_start, screen_height - aoi_height))
    y_end = max(0, min(y_end, screen_height))
    
    return [x_start, x_end, y_start, y_end]


# Initialising the eyetracker

found_eyetrackers = tr.find_all_eyetrackers()
# We will just use the first one
Eyetracker = found_eyetrackers[0]

# Create an empty list we will append our data to
gaze_data_buffer = []

# Setting psychopy specific variables

win = visual.Window(size=winsize,units='pix',fullscr=True, screen = 2, color='black')

# Fixation circle
fixation = visual.Circle(win, radius=10, lineColor='white', fillColor=None, pos=(0, 0))

# Shapes for test phase
circle = visual.Circle(win, radius=10, fillColor='white', lineColor='white')
square = visual.Rect(win, width=20, height=20, fillColor='white', lineColor='white')

# Timing in milliseconds
time_in_roi = 800  # Fixation ROI time
timeout_limit = 5000  # Timeout for response
inter_trial_interval = 1000  # Blank interval between trials


# Colors for shapes
colors = ['red', 'green', 'blue']

# Trial conditions
trial_conditions = []
for color1 in colors:
    for color2 in colors:
        if color1 != color2:
            trial_conditions.extend([{'circle_color': color1, 'square_color': color2, 'target': 'circle'},
                                     {'circle_color': color2, 'square_color': color1, 'target': 'square'}])

data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Experiment handler
thisExp = data.ExperimentHandler(name=experiment_name, version='1.0',
                                 extraInfo={'participant': participant_id},
                                 runtimeInfo=None,
                                 originPath=None,
                                 savePickle=True, saveWideText=True,
                                 dataFileName=os.path.join(data_folder, f'{experiment_name}_{participant_id}'))

# Setup trial handler
trials = data.TrialHandler(trial_conditions, nReps=1, method='random',
                           extraInfo={}, originPath=-1,
                           name='trials')

# Start recording
Eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

# Finding the Area of Interest for Fixation
x_left, x_right, y_bottom, y_top = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20,20], position_of_interest=[0,0])
print("fixation - area of interest : ",x_left, x_right, y_bottom, y_top)

for thisTrial in trials:
    # Show fixation
    fixation.fillColor = None
    trigger = "fixation"
    fixation.draw()
    win.flip()
    
    # Wait for mouse in fixation ROI
    timer = core.Clock()
    while True:
        if r[0] == 1 and x_left <= r[1] <= x_right and y_bottom <= r[2] <= y_top:
            fixation.fillColor = 'white'
            trigger = "gaze on fixation"
            fixation.draw()
            win.flip()
            break
        elif not (r[0] == 1 and x_left <= r[1] <= x_right and y_bottom <= r[2] <= y_top):
            timer.reset()
        fixation.draw()
        win.flip()
    
    # Reset timer for response time
    response_timer = core.Clock()
    
    # Set colors for this trial
    circle.fillColor = thisTrial['circle_color']
    circle.lineColor = thisTrial['circle_color']
    square.fillColor = thisTrial['square_color']
    square.lineColor = thisTrial['square_color']
    
    # Display shapes on left and right
    circle.pos = (-300, 0) if thisTrial['target'] == 'circle' else (300, 0)
    square.pos = (300, 0) if thisTrial['target'] == 'circle' else (-300, 0)

    # Define ROIs for targets
    circle_roi = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20, 20], position_of_interest=[-300 if thisTrial['target'] == 'circle' else 300, 0])
    square_roi = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20, 20], position_of_interest=[300 if thisTrial['target'] == 'circle' else -300, 0])

    # Unpack ROI coordinates
    circle_x_left, circle_x_right, circle_y_bottom, circle_y_top = circle_roi
    square_x_left, square_x_right, square_y_bottom, square_y_top = square_roi
    
    # Draw shapes and fixation
    fixation.draw()
    circle.draw()
    square.draw()
    trigger = "Circle and Square on Screen" 
    win.flip()
    
    # Wait for response or timeout
    correct_response = False
    errant_response = False
    # while response_timer.getTime() * 1000 < timeout_limit:
    while True:
        if r[0] == 1:  # Check if right eye data is valid
            if thisTrial['target'] == 'circle' and circle_x_left <= r[1] <= circle_x_right and circle_y_bottom <= r[2] <= circle_y_top:
                correct_response = True
                break
            elif thisTrial['target'] == 'square' and square_x_left <= r[1] <= square_x_right and square_y_bottom <= r[2] <= square_y_top:
                correct_response = True
                break
            elif (thisTrial['target'] == 'circle' and square_x_left <= r[1] <= square_x_right and square_y_bottom <= r[2] <= square_y_top) or \
             (thisTrial['target'] == 'square' and circle_x_left <= r[1] <= circle_x_right and circle_y_bottom <= r[2] <= circle_y_top):
                errant_response = True
                break
        else:
            print('Eye not on screen.')

    if response_timer.getTime() * 1000 >= timeout_limit:
        break  # Timeout

    # Redraw to keep the screen updated
    fixation.draw()
    circle.draw()
    square.draw()
    win.flip()

    if response_timer.getTime() * 1000 >= timeout_limit:
        break  # Timeout

    # Redraw to keep the screen updated
    fixation.draw()
    circle.draw()
    square.draw()
    win.flip()
    
    # Record response data
    response_time = response_timer.getTime() * 1000
    if correct_response:
        thisExp.addData('response', 'correct')
    elif errant_response:
        thisExp.addData('response', 'errant')
    else:
        # Display "Miss" feedback
        miss_feedback = visual.TextStim(win, text="Miss", pos=(0, 0))
        miss_feedback.draw()
        win.flip()
        core.wait(1)  # Display for 1000 ms
        thisExp.addData('response', 'miss')
    
    thisExp.addData('response_time', response_time)
    thisExp.addData('circle_color', thisTrial['circle_color'])
    thisExp.addData('square_color', thisTrial['square_color'])
    thisExp.addData('target', thisTrial['target'])
    
    # Inter-trial blank screen
    win.flip()
    core.wait(inter_trial_interval / 1000)

    # Move to next trial
    thisExp.nextEntry()

    # Save data to file after each trial
    write_buffer_to_file(gaze_data_buffer, f'{experiment_name}_{participant_id}_eye_data.csv')

    ### Check for closing experiment
    keys = event.getKeys()  # collect list of pressed keys
    if 'escape' in keys:
        win.close()  # close window
        Eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)  # unsubscribe eye tracking
        core.quit()  # stop study

# Clean up
thisExp.saveAsWideText(f'{experiment_name}_{participant_id}.csv', delim=',')
thisExp.saveAsPickle(f'{experiment_name}_{participant_id}.pkl')
Eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)  # unsubscribe eye tracking
win.close()
core.quit()