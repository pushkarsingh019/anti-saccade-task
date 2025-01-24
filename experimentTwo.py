# Integrated Script for Training (With Reward) and Test Phase
# Pushkar Singh, 24th January, 2025

from psychopy import visual, core, event, data, prefs, gui
from psychopy.event import Mouse
import random
import os
import pandas as pd
import numpy as np
prefs.hardware['audioLib'] = ['PTB']
from psychopy import sound
import tobii_research as tr

# Global variables
r = np.zeros(3)  # Right eye data storage
participant_id = 456
winsize = [1366,768]
experiment_name = 'Integrated_Experiment_Reward'

# Function definitions
def gaze_data_callback(gaze_data):
    global trigger, gaze_data_buffer, winsize, r

    if len(trigger)==0:
        ev = ''
    else:
        ev = trigger
        trigger=[]
    
    t  = gaze_data.system_time_stamp / 1000.0
    lx = gaze_data.left_eye.gaze_point.position_on_display_area[0] * winsize[0]
    ly = winsize[1] - gaze_data.left_eye.gaze_point.position_on_display_area[1] * winsize[1]
    lp = gaze_data.left_eye.pupil.diameter
    lv = gaze_data.left_eye.gaze_point.validity
    rx = gaze_data.right_eye.gaze_point.position_on_display_area[0] * winsize[0]
    ry = winsize[1] - gaze_data.right_eye.gaze_point.position_on_display_area[1] * winsize[1]
    rp = gaze_data.right_eye.pupil.diameter
    rv = gaze_data.right_eye.gaze_point.validity
        
    gaze_data_buffer.append((t,lx,ly,lp,lv,rx,ry,rp,rv,ev))
    r[0] = rv
    r[1] = rx
    r[2] = ry

def write_buffer_to_file(buffer, output_path):
    buffer_copy = buffer[:]
    buffer.clear()
    
    columns = ['time', 'L_X', 'L_Y', 'L_P', 'L_V', 
               'R_X', 'R_Y', 'R_P', 'R_V', 'Event']

    out = pd.DataFrame(buffer_copy, columns=columns)
    
    file_exists = not os.path.isfile(output_path)
    
    out.to_csv(output_path, mode='a', index =False, header = file_exists)

def get_area_of_interest(screen_resolution, area_of_interest, position_of_interest):
    screen_width, screen_height = screen_resolution
    aoi_width, aoi_height = area_of_interest
    aoi_x, aoi_y = position_of_interest
    
    x_start = screen_width // 2 + aoi_x - aoi_width // 2
    x_end = x_start + aoi_width
    y_start = screen_height // 2 + aoi_y - aoi_height // 2
    y_end = y_start + aoi_height
    
    x_start = max(0, min(x_start, screen_width - aoi_width))
    x_end = max(0, min(x_end, screen_width))
    y_start = max(0, min(y_start, screen_height - aoi_height))
    y_end = max(0, min(y_end, screen_height))
    
    return [x_start, x_end, y_start, y_end]

# Setup for eyetracker
found_eyetrackers = tr.find_all_eyetrackers()
Eyetracker = found_eyetrackers[0]
gaze_data_buffer = []

# PsychoPy setup
win = visual.Window(size=winsize,units='pix',fullscr=True, screen = 2, color='black')

# Define shapes
fixation_diameter = 20
fixation = visual.Circle(win, radius=fixation_diameter/2, lineColor='white', fillColor=None, pos=(0, 0))

circle_diameter = 20
circle = visual.Circle(win, radius=circle_diameter/2, fillColor='white', lineColor='white')

square = visual.Rect(win, width=20, height=20, fillColor='white', lineColor='white')

# Timing in milliseconds
time_in_roi = 500  # Fixation ROI time
timeout_limit = 5000  # Timeout for response
inter_trial_interval = 1000  # Blank interval between trials

# Colors - Assuming 'red' is high value, 'blue' is low value
colors = {'high_value': 'red', 'low_value': 'blue'}

# Reward images
high_value_star = visual.ImageStim(win, image='high_value_star.png', pos=(0, 0), size=(100, 100))
low_value_star = visual.ImageStim(win, image='low_value_star.png', pos=(0, 0), size=(50, 50))  # Smaller for low value

# Data folder creation
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

# Experiment handler setup
thisExp = data.ExperimentHandler(name=experiment_name, version='1.0',
                                 extraInfo={'participant': participant_id},
                                 runtimeInfo=None,
                                 originPath=None,
                                 savePickle=True, saveWideText=True,
                                 dataFileName=os.path.join(data_folder, f'{experiment_name}_{participant_id}'))

# Training Phase (With Reward)
training_conditions = [{'color': color, 'value': value} for value, color in colors.items()] * 10  # Example: 10 trials per color
training_trials = data.TrialHandler(training_conditions, nReps=1, method='random',
                                    extraInfo={}, originPath=-1,
                                    name='training_trials')

Eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

# Training Phase Loop
for thisTrial in training_trials:
    # Fixation
    fixation.fillColor = None
    trigger = "fixation"
    fixation.draw()
    win.flip()
    
    fixation_frames = 0
    frames_per_500ms = int(0.5 / win.monitorFramePeriod)
    
    while True:
        if r[0] == 1 and get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[0] <= r[1] <= get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[1] and get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[2] <= r[2] <= get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[3]:
            fixation_frames += 1
            if fixation_frames >= frames_per_500ms:
                fixation.fillColor = 'white'
                trigger = "gaze on fixation"
                fixation.draw()
                win.flip()
                break
        else:
            fixation_frames = 0
        fixation.draw()
        win.flip()
    
    # Display shape with trial color
    circle.fillColor = thisTrial['color']
    circle.lineColor = thisTrial['color']
    circle.pos = (0, 0)
    circle.draw()
    trigger = "Circle on Screen" 
    win.flip()
    
    # Wait for response or timeout
    response_frames = 0
    frames_timeout_limit = int(timeout_limit / 1000 / win.monitorFramePeriod)
    
    while True:
        response_frames += 1
        if response_frames >= frames_timeout_limit:
            break  # Timeout
        circle.draw()
        win.flip()
    
    # Present reward
    if thisTrial['value'] == 'high_value':
        reward_image = high_value_star
    else:
        reward_image = low_value_star
    
    reward_image.draw()
    win.flip()
    core.wait(1)  # Display reward for 1000ms

    thisExp.addData('phase', 'training_with_reward')
    thisExp.addData('color', thisTrial['color'])
    thisExp.addData('value', thisTrial['value'])
    thisExp.addData('response_time', response_frames * win.monitorFramePeriod * 1000)
    thisExp.nextEntry()

    write_buffer_to_file(gaze_data_buffer, os.path.join(data_folder, f'{experiment_name}_{participant_id}_eye_data.csv'))

# Test Phase
# Here, we'll use the same colors for simplicity, but you can adjust based on your experiment's needs
test_conditions = []
for target_color in colors.keys():
    for distractor_color in colors.keys():
        if target_color != distractor_color:  # Ensure target and distractor are different
            test_conditions.append({'target_color': target_color, 'distractor_color': distractor_color})

test_trials = data.TrialHandler(test_conditions, nReps=1, method='random',
                                extraInfo={}, originPath=-1,
                                name='test_trials')

for thisTrial in test_trials:
    # Fixation (same as training)
    fixation.fillColor = None
    trigger = "fixation"
    fixation.draw()
    win.flip()
    
    fixation_frames = 0
    frames_per_500ms = int(0.5 / win.monitorFramePeriod)
    
    while True:
        if r[0] == 1 and get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[0] <= r[1] <= get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[1] and get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[2] <= r[2] <= get_area_of_interest(winsize, [fixation_diameter, fixation_diameter], [0,0])[3]:
            fixation_frames += 1
            if fixation_frames >= frames_per_500ms:
                fixation.fillColor = 'white'
                trigger = "gaze on fixation"
                fixation.draw()
                win.flip()
                break
        else:
            fixation_frames = 0
        fixation.draw()
        win.flip()
    
    # Display shapes with trial colors
    circle.fillColor = colors[thisTrial['target_color']]
    circle.lineColor = colors[thisTrial['target_color']]
    square.fillColor = colors[thisTrial['distractor_color']]
    square.lineColor = colors[thisTrial['distractor_color']]
    
    circle.pos = (-300, 0)
    square.pos = (300, 0)
    
    fixation.draw()
    circle.draw()
    square.draw()
    trigger = "Circle and Square on Screen" 
    win.flip()
    
    # Wait for response or timeout
    correct_response = False
    errant_response = False
    response_frames = 0
    frames_timeout_limit = int(timeout_limit / 1000 / win.monitorFramePeriod)
    
    circle_roi = get_area_of_interest(winsize, [circle_diameter, circle_diameter], circle.pos)
    square_roi = get_area_of_interest(winsize, [20, 20], square.pos)
    
    while True:
        if r[0] == 1:  
            if circle_roi[0] <= r[1] <= circle_roi[1] and circle_roi[2] <= r[2] <= circle_roi[3]:
                correct_response = True
                break
            elif square_roi[0] <= r[1] <= square_roi[1] and square_roi[2] <= r[2] <= square_roi[3]:
                errant_response = True
                break
        
        response_frames += 1
        if response_frames >= frames_timeout_limit:
            break  # Timeout

        fixation.draw()
        circle.draw()
        square.draw()
        win.flip()
    
    # Record response data
    response_time = response_frames * win.monitorFramePeriod * 1000
    if correct_response:
        thisExp.addData('response', 'correct')
    elif errant_response:
        thisExp.addData('response', 'errant')
    else:
        thisExp.addData('response', 'miss')
    
    thisExp.addData('phase', 'test')
    thisExp.addData('response_time', response_time)
    thisExp.addData('target_color', thisTrial['target_color'])
    thisExp.addData('distractor_color', thisTrial['distractor_color'])
    thisExp.nextEntry()

    write_buffer_to_file(gaze_data_buffer, os.path.join(data_folder, f'{experiment_name}_{participant_id}_eye_data.csv'))

    # Check for closing experiment
    keys = event.getKeys()  
    if 'escape' in keys:
        win.close()
        Eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
        core.quit()

# Cleanup
Eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
win.close()
core.quit()