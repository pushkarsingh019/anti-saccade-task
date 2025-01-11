from psychopy import visual, core, event, data
from psychopy.event import Mouse
import random

# For Madhav
participant_id = 456

# Window setup
win = visual.Window(size=(800, 600), units='pix')

# Fixation circle
fixation = visual.Circle(win, radius=10, lineColor='black', fillColor=None, pos=(0, 0))

# Shapes for test phase
circle = visual.Circle(win, radius=10, fillColor='white', lineColor='white')
square = visual.Rect(win, width=20, height=20, fillColor='white', lineColor='white')

# Mouse setup
mouse = Mouse(win=win)

# Timing in milliseconds
time_in_roi = 800  # Fixation ROI time
timeout_limit = 1000  # Timeout for response
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

# Experiment handler
thisExp = data.ExperimentHandler(name='MyTestExperiment', version='1.0',
                                 extraInfo={'participant': participant_id},
                                 runtimeInfo=None,
                                 originPath=None,
                                 savePickle=True, saveWideText=True,
                                 dataFileName='my_test_experiment_data')

# Setup trial handler
trials = data.TrialHandler(trial_conditions, nReps=1, method='random',
                           extraInfo={}, originPath=-1,
                           name='trials')

for thisTrial in trials:
    # Show fixation
    fixation.fillColor = None
    fixation.draw()
    win.flip()
    
    # Wait for mouse in fixation ROI
    timer = core.Clock()
    while True:
        if abs(mouse.getPos()[0]) <= 10 and abs(mouse.getPos()[1]) <= 10 and timer.getTime() * 1000 > time_in_roi:
            fixation.fillColor = 'white'
            fixation.draw()
            win.flip()
            break
        elif not (abs(mouse.getPos()[0]) <= 10 and abs(mouse.getPos()[1]) <= 10):
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
    
    # Draw shapes and fixation
    fixation.draw()
    circle.draw()
    square.draw()
    win.flip()
    
    # Wait for response or timeout
    correct_response = False
    errant_response = False
    while response_timer.getTime() * 1000 < timeout_limit:
        mouse_pos = mouse.getPos()
        if thisTrial['target'] == 'circle' and mouse_pos[0] <= -300:
            correct_response = True
            break
        elif thisTrial['target'] == 'square' and mouse_pos[0] >= 300:
            correct_response = True
            break
        elif (thisTrial['target'] == 'circle' and mouse_pos[0] >= 300) or (thisTrial['target'] == 'square' and mouse_pos[0] <= -300):
            errant_response = True
            break
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

# Clean up
thisExp.saveAsWideText('my_test_experiment_data.csv', delim=',')
thisExp.saveAsPickle('my_test_experiment_data.pkl')
win.close()
core.quit()