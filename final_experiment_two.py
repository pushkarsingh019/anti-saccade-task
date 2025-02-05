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
buffer = 40


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
fixation_diameter = 20 
fixation = visual.Circle(win, radius=fixation_diameter/2, lineColor='white', fillColor=None, pos=(0, 0))


# Blue square for new task
square = visual.Rect(win, width=50, height=50, fillColor='blue', lineColor='blue')
circle = visual.Circle(win, radius=25, fillColor='white', lineColor='white')

# Timing in milliseconds
time_in_roi = 250 # Fixation ROI time
time_in_new_roi = 1000  # Antisaccade ROI time.
inter_trial_interval = 1000
timeout_limit = 5000

data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)

colors = ["red", "green", "blue"]
high_value_color = np.random.choice(colors)
# remove high_value_color to get low_value_color
colors.remove(high_value_color)
low_value_color = np.random.choice(colors)
colors.remove(low_value_color)
control_color = colors[0]

# Trial conditions for training
trial_conditions_training = [{'trial_num': i+1} for i in range(10)]

# Trial conditions for test
trial_conditions_test = []
colors = ["red", "green", "blue"]
for color1 in colors:
    for color2 in colors:
        if color1 != color2:
            trial_conditions_test.append({'circle_color': color1, 'square_color': color2, 'target': 'circle'})

# Experiment handler
thisExp = data.ExperimentHandler(name=experiment_name, version='1.0',
                                 extraInfo={'participant': participant_id},
                                 runtimeInfo=None,
                                 originPath=None,
                                 savePickle=True, saveWideText=True,
                                 dataFileName=os.path.join(data_folder, f'{experiment_name}_{participant_id}'))

# Setup trial handler 
training_trials = data.TrialHandler(trial_conditions_training, nReps=1, method='random',
                           extraInfo={}, originPath=-1,
                           name='training_trials')


# Setup trial handler
test_trials = data.TrialHandler(trial_conditions_test, nReps=1, method='random',
                           extraInfo={}, originPath=-1,
                           name='trials')

# Start recording
Eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)

 # setting AOI boundaries for fixation
 # 
x_left, x_right, y_bottom, y_top = get_area_of_interest(screen_resolution=winsize, area_of_interest=[fixation_diameter + buffer, fixation_diameter + buffer], position_of_interest=[0,0])
print(x_left, x_right, y_bottom, y_top)

thisExp.addData('high_value_color', high_value_color)
thisExp.addData('low_value_color', low_value_color)
thisExp.addData('control_color', control_color)

for thisTrial in training_trials:
    thisExp.addData("phase", "training")
    # Show hollow fixation
    fixation.fillColor = None
    trigger = "fixation on screen"
    fixation.draw()
    win.flip()
    
    # Wait for eye in fixation ROI
    timer = core.Clock()
    timer.reset()

    while True:
        if r[0] == 1 and x_left <= r[1] <= x_right and y_bottom <= r[2] <= y_top:
            if timer.getTime() * 1000 >= time_in_roi:
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

    # randomly choosing the colour of the square.
    square_color = np.random.choice([high_value_color, low_value_color], p=[0.5, 0.5])
    square.fillColor = square_color
    square.lineColor = square_color

    if square_color == high_value_color:
        thisExp.addData('colour_condition', 'high_value_color')
        thisExp.addData('square_color', high_value_color)
    else:
        thisExp.addData('colour_condition', 'low_value_color')
        thisExp.addData('square_color', low_value_color)
    
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
    
    # Reset the timer when the square appears
    square_timer = core.Clock()
    square_timer.reset()  # Start timing from when the square is shown

    while True:
        if (side == 'left' and r[0] == 1 and r[1] >= x_lim) or (side == 'right' and r[0] == 1 and r[1] <= x_lim):
            # Measure the time since the square was displayed
            reaction_time = square_timer.getTime() * 1000
        
            # Check if the eye has stayed on the opposite side long enough
            if reaction_time >= time_in_new_roi:
                trigger = "antisaccade"
                thisExp.addData('reaction_time', reaction_time)
                thisExp.addData('square_side', side)
                break
    # Redraw to keep the screen updated
    fixation.draw()
    square.draw()
    win.flip()
    
    # Reset fixation to hollow for next trial
    fixation.fillColor = None

    if square_color == high_value_color:
        # Display star image for 1500s as reward
        trigger = "reward"
        star_image = visual.ImageStim(win, image='star.jpg', pos=(0, 0), size=(500, 500))
        star_image.draw()
        win.flip()
        core.wait(1.5)  # Display for 1000 ms
    else:
        trigger = "no_reward"
    
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

# Add a break before starting the test phase
break_text = visual.TextStim(win, text="Test phase will begin shortly.", pos=(0, 0), color='white')
break_text.draw()
win.flip()

# Wait for 10 seconds
core.wait(5)

# Clear the screen before starting the test phase
win.flip()

# Test Phase

missed_trials = 0

for thisTrial in test_trials:
    thisExp.addData("phase", "test")
    # Show fixation
    fixation.fillColor = None
    trigger = "fixation"
    fixation.draw()
    win.flip()
    
    # Wait for eye in fixation ROI for a certain number of frames
    fixation_frames = 0
    frames_per_500ms = int(0.5 / win.monitorFramePeriod)  # Convert 500ms to frames
    
    while True:
        if r[0] == 1 and x_left <= r[1] <= x_right and y_bottom <= r[2] <= y_top:
            fixation_frames += 1
            if fixation_frames >= frames_per_500ms:
                fixation.fillColor = 'white'
                trigger = "gaze on fixation"
                fixation.draw()
                win.flip()
                break
        else:
            fixation_frames = 0  # Reset frame count if gaze leaves ROI
        fixation.draw()
        win.flip()
    
    # Reset timer for response time
    response_timer = core.Clock()
    response_timer.reset()
    
    # Set colors for this trial
    circle.fillColor = thisTrial['circle_color']
    circle.lineColor = thisTrial['circle_color']
    square.fillColor = thisTrial['square_color']
    square.lineColor = thisTrial['square_color']
    
    circle.pos = [-300, 0] if random.choice([True, False]) else [300, 0]
    square.pos = [300, 0] if circle.pos[0] == -300 else [-300, 0]

    # Define ROIs for targets
    circle_roi = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20, 20], position_of_interest=circle.pos)
    square_roi = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20, 20], position_of_interest=square.pos)

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
    response_frames = 0
    frames_timeout_limit = int(timeout_limit / 1000 / win.monitorFramePeriod)  # Convert timeout_limit to frames
    
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

        response_frames += 1
        if response_frames >= frames_timeout_limit:
            break  # Timeout

        # Redraw to keep the screen updated
        fixation.draw()
        circle.draw()
        square.draw()
        win.flip()
    
    # Record response data
    response_time = response_frames * win.monitorFramePeriod * 1000  # Convert back to milliseconds
    if correct_response:
        thisExp.addData('response', 'correct')
    elif errant_response:
        thisExp.addData('response', 'errant')
    else:
        # Display "Miss" feedback
        missed_trials = missed_trials + 1
        miss_feedback = visual.TextStim(win, text="Miss", pos=(0, 0))
        miss_feedback.draw()
        win.flip()
        core.wait(1)  # Display for 1000 ms
        thisExp.addData('response', 'miss')
    
    thisExp.addData('response_time', response_time)
    thisExp.addData('circle_color', thisTrial['circle_color'])
    thisExp.addData('square_color', thisTrial['square_color'])
    thisExp.addData('target', thisTrial['target'])

    # checking the condition
    if thisTrial['circle_color'] == high_value_color:
        thisExp.addData('target_condition', 'high_value_color')
    elif thisTrial['circle_color'] == low_value_color:
        thisExp.addData('target_condition', 'low_value_color')
    elif thisTrial['circle_color'] == control_color:
        thisExp.addData('target_condition', 'control_color')
    else:
        thisExp.addData('target_condition', 'unknown_color')
    
    # storing the condition of the square
    if thisTrial['square_color'] == high_value_color:
        thisExp.addData('distractor_condition', 'high_value_color')
    elif thisTrial['square_color'] == low_value_color:
        thisExp.addData('distractor_condition', 'low_value_color')
    elif thisTrial['square_color'] == control_color:
        thisExp.addData('distractor_condition', 'control_color')
    else:
        thisExp.addData('distractor_condition', 'unknown_color')
    
    # Inter-trial blank screen
    win.flip()
    core.wait(inter_trial_interval / 1000)

    # Move to next trial
    thisExp.nextEntry()

    # Save data to file after each trial
    write_buffer_to_file(gaze_data_buffer, os.path.join(data_folder,f'{experiment_name}_{participant_id}_eye_data.csv'))

    ### Check for closing experiment
    keys = event.getKeys()  # collect list of pressed keys
    if 'escape' in keys:
        win.close()  # close window
        Eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)  # unsubscribe eye tracking
        core.quit()  # stop study

while missed_trials > 0:
    print("Looping over missed trials.")
    thisExp.addData("phase", "test")
    # Show fixation
    fixation.fillColor = None
    trigger = "fixation"
    fixation.draw()
    win.flip()
    
    # Wait for eye in fixation ROI for a certain number of frames
    fixation_frames = 0
    frames_per_500ms = int(0.5 / win.monitorFramePeriod)  # Convert 500ms to frames
    
    while True:
        if r[0] == 1 and x_left <= r[1] <= x_right and y_bottom <= r[2] <= y_top:
            fixation_frames += 1
            if fixation_frames >= frames_per_500ms:
                fixation.fillColor = 'white'
                trigger = "gaze on fixation"
                fixation.draw()
                win.flip()
                break
        else:
            fixation_frames = 0  # Reset frame count if gaze leaves ROI
        fixation.draw()
        win.flip()
    
    # Reset timer for response time
    response_timer = core.Clock()
    response_timer.reset()

    # Generate random colors for the retry trial
    random_circle_color = random.choice(colors)
    random_square_color = random.choice([color for color in colors if color != random_circle_color])
    
    # Set colors for this trial
    circle.fillColor = random_circle_color
    circle.lineColor = random_circle_color
    square.fillColor = random_square_color
    square.lineColor = random_square_color
    
    # Display shapes on left and right (circle can be on left or right equally)
    circle.pos = [-300, 0] if random.choice([True, False]) else [300, 0]
    square.pos = [300, 0] if circle.pos[0] == -300 else [-300, 0]

    # Define ROIs for targets
    circle_roi = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20, 20], position_of_interest=circle.pos)
    square_roi = get_area_of_interest(screen_resolution=winsize, area_of_interest=[20, 20], position_of_interest=square.pos)

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
    response_frames = 0
    frames_timeout_limit = int(timeout_limit / 1000 / win.monitorFramePeriod)  # Convert timeout_limit to frames
    
    while True:
        if r[0] == 1:  # Check if right eye data is valid
            if circle_x_left <= r[1] <= circle_x_right and circle_y_bottom <= r[2] <= circle_y_top:
                correct_response = True
                break
            elif square_x_left <= r[1] <= square_x_right and square_y_bottom <= r[2] <= square_y_top:
                errant_response = True  # Wrong choice (chose square instead of circle)
                break
        else:
            print('Eye not on screen.')

        response_frames += 1
        if response_frames >= frames_timeout_limit:
            break  # Timeout

        # Redraw to keep the screen updated
        fixation.draw()
        circle.draw()
        square.draw()
        win.flip()
    
    # Record response data
    response_time = response_frames * win.monitorFramePeriod * 1000  # Convert back to milliseconds
    if correct_response:
        thisExp.addData('response', 'correct')
        missed_trials = missed_trials - 1
    elif errant_response:
        missed_trials = missed_trials - 1
        thisExp.addData('response', 'errant')
    else:
        missed_trials = missed_trials + 1
        miss_feedback = visual.TextStim(win, text="Miss", pos=(0, 0))
        miss_feedback.draw()
        win.flip()
        core.wait(1)  # Display for 1000 ms
        thisExp.addData('response', 'miss')
    
    thisExp.addData('response_time', response_time)
    thisExp.addData('circle_color', random_circle_color)
    thisExp.addData('square_color', random_square_color)
    thisExp.addData('target', thisTrial['target'])

    # checking the condition
    if random_circle_color == high_value_color:
        thisExp.addData('target_condition', 'high_value_color')
    elif random_circle_color == low_value_color:
        thisExp.addData('target_condition', 'low_value_color')
    elif random_circle_color == control_color:
        thisExp.addData('target_condition', 'control_color')
    else:
        thisExp.addData('target_condition', 'unknown_color')
    
    # storing the condition of the square
    if random_square_color == high_value_color:
        thisExp.addData('distractor_condition', 'high_value_color')
    elif random_square_color == low_value_color:
        thisExp.addData('distractor_condition', 'low_value_color')
    elif random_square_color == control_color:
        thisExp.addData('distractor_condition', 'control_color')
    else:
        thisExp.addData('distractor_condition', 'unknown_color')
    
    # Inter-trial blank screen
    win.flip()
    core.wait(inter_trial_interval / 1000)

    # Move to next trial
    thisExp.nextEntry()

    # Save data to file after each trial
    write_buffer_to_file(gaze_data_buffer, os.path.join(data_folder,f'{experiment_name}_{participant_id}_eye_data.csv'))

    ### Check for closing experiment
    keys = event.getKeys()  # collect list of pressed keys
    if 'escape' in keys:
        win.close()  # close window
        Eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)  # unsubscribe eye tracking
        core.quit()  # stop study


# Clean up
Eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)  # unsubscribe eye tracking
win.close()
core.quit()


