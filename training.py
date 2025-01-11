from psychopy import visual, core, event, data, gui
from psychopy.event import Mouse
import random

# For Madhav
participant_id = 123

# Window setup
win = visual.Window(size=(800, 600), units='pix')

# Fixation circle
fixation = visual.Circle(win, radius=10, lineColor='white', fillColor=None, pos=(0, 0))

# Blue square for new task
square = visual.Rect(win, width=50, height=50, fillColor='blue', lineColor='blue')

# Mouse setup
mouse = Mouse(win=win)

# Timing in milliseconds
time_in_roi = 800
time_in_new_roi = 1000  # New ROI time in milliseconds
inter_trial_interval = 1000

# Trial conditions
trial_conditions = [{'trial_num': i+1} for i in range(5)]  # Example condition for 5 trials

# Experiment handler
thisExp = data.ExperimentHandler(name='MyExperiment', version='1.0',
                                 extraInfo={'participant': participant_id},
                                 runtimeInfo=None,
                                 originPath=None,
                                 savePickle=True, saveWideText=True,
                                 dataFileName='my_experiment_data')

# Setup trial handler
trials = data.TrialHandler(trial_conditions, nReps=1, method='random',
                           extraInfo={}, originPath=-1,
                           name='trials')


for thisTrial in trials:
    # Show hollow fixation
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
    
    # Reset timer for new reaction time
    square_timer = core.Clock()  # Timer for when the square is displayed
    
    # Display blue square randomly on left or right
    side = random.choice(['left', 'right'])
    square_pos = (-300, 0) if side == 'left' else (300, 0)
    square.pos = square_pos
    
    # Draw both fixation (which is now white) and square
    fixation.draw()
    square.draw()
    win.flip()
    
    # Wait for mouse to move to opposite side (or beyond), measure reaction time
    opposite_side = 300 if side == 'left' else -300
    while True:
        if (side == 'left' and mouse.getPos()[0] >= 300) or (side == 'right' and mouse.getPos()[0] <= -300):
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
    
    # Inter-trial blank screen
    win.flip()
    core.wait(inter_trial_interval / 1000)

    # Move to next trial
    thisExp.nextEntry()

# Clean up
thisExp.saveAsWideText('my_experiment_data.csv', delim=',')
thisExp.saveAsPickle('my_experiment_data.pkl')
win.close()
core.quit()