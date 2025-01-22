# importing modules
import os
import pandas as pd
import numpy as np
from psychopy import core, event, visual, prefs, data, gui
prefs.hardware['audioLib'] = ['PTB']
from psychopy import sound
import tobii_research as tr
import random

# since all checks happen only with right eye cooridinates, this variable stores the right eye data. The structure being : r.validity , r.x_cooridinate, r.y_coordinate
r = np.zeros(3)

# For Madhav
participant_id = 123
winsize = [1366,768]
experiment_name = 'training_phase'


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


# finding and initialising the eyetracker
found_eyetrackers = tr.find_all_eyetrackers()

# We will just use the first one
Eyetracker = found_eyetrackers[0]

# Create an empty list we will append our data to
gaze_data_buffer = []

# Setting psychopy specific variables

# Window setup
win = visual.Window(size=winsize,units='pix',fullscr=True, screen = 2, color='black')

# Fixation circle
fixation = visual.Circle(win, radius=10, lineColor='white', fillColor=None, pos=(0, 0))

# Blue square for new task
square = visual.Rect(win, width=50, height=50, fillColor='blue', lineColor='blue')

# Timing in milliseconds
time_in_roi = 800
time_in_new_roi = 1000  # New ROI time in milliseconds
inter_trial_interval = 1000

# Trial conditions
trial_conditions = [{'trial_num': i+1} for i in range(10)]  # Example condition for 5 trials

# Experiment handler
thisExp = data.ExperimentHandler(name=experiment_name, version='1.0',
                                 extraInfo={'participant': participant_id},
                                 runtimeInfo=None,
                                 originPath=None,
                                 savePickle=True, saveWideText=True,
                                 dataFileName=f'{experiment_name}_{participant_id}')

# Setup trial handler 
trials = data.TrialHandler(trial_conditions, nReps=1, method='random',
                           extraInfo={}, originPath=-1,
                           name='trials')


# Start recording
Eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

 # setting AOI boundaries for fixation
 # 
x_left, x_right, y_bottom, y_top = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20,20], position_of_interest=[0,0])
print(x_left, x_right, y_bottom, y_top)

for thisTrial in trials:
    # Show hollow fixation
    fixation.fillColor = None
    trigger = "fixation on screen"
    fixation.draw()
    win.flip()
    
    # Wait for eye in fixation ROI
    timer = core.Clock()
    while True:
        if r[0] == 1 and x_left <= r[1] <= x_right and y_bottom <= r[2] <= y_top:
            print(timer.getTime())
            fixation.fillColor = 'white'
            trigger = "gaze on fixation"
            fixation.draw()
            win.flip()
            break
        elif not (r[0] == 1 and x_left <= r[1] <= x_right and y_bottom <= r[2] <= y_top):
            timer.reset()
        fixation.draw()
        win.flip()
    
    # Reset timer for new reaction time
    square_timer = core.Clock()  # Timer for when the square is displayed
    
    # Display blue square randomly on left or right
    side = random.choice(['left', 'right'])
    square_pos = (-300, 0) if side == 'left' else (300, 0)
    square.pos = square_pos
    x_lim = 0
    if square_pos == (-300, 0):
        x_start, x_end, y_bottom, y_top = get_area_of_interest(winsize, [50,50], [300, 0])
        x_lim = x_end
    else:
        x_start, x_end, y_bottom, y_top = get_area_of_interest(winsize, [50,50], [-300, 0])
        x_lim = x_start

    
    # Draw both fixation (which is now white) and square
    fixation.draw()
    trigger = "target"
    square.draw()
    win.flip()
    
    # Wait for eye to move to opposite side (or beyond), measure reaction time
    while True:
        if (side == 'left' and r[0] == 1 and r[1] >= x_lim) or (side == 'right' and  r[0] == 1 and r[1] <= x_lim):
            trigger = "antisaccade"
            reaction_time = square_timer.getTime() * 1000  # Time from square display to ROI entry
            thisExp.addData('reaction_time', reaction_time)
            thisExp.addData('square_side', side)
            if reaction_time >= time_in_new_roi:
                break
        fixation.draw()
        square.draw()
        win.flip()
    
    # Reset fixation to hollow for next trial
    fixation.fillColor = None

    # Display star image for 1000ms as reward
    star_image = visual.ImageStim(win, image='star.jpg', pos=(0, 0), size=(500, 500))
    star_image.draw()
    win.flip()
    core.wait(1)  # Display for 1000 ms
    
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