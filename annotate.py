import cv2, os, sys
#import time
import logging
import argparse

from collections   import OrderedDict

def parse_arguments():
    ap = argparse.ArgumentParser()

    ap.add_argument('-v', '--video'  , type=str, help='path to input video file' )
    ap.add_argument('-t', '--tracker', type=str, help='object tracking algorithm')
    ap.add_argument('-f', '--fps'    , type=str, help='frame per second'         )

    args = vars(ap.parse_args())
    
    video_path   = args['video'  ]
    tracker_name = args['tracker']
    fps          = args['fps'    ]

    if tracker_name is None:
        tracker_name = 'csrt'
        print('Since you did not specify tracking algorithm... Will use default tracking algorithm = ', tracker_name)
    if fps is None:
        fps = 10
        print('Since you did not specify fps... Running at default fps = ', fps)
    else:
        fps = int(fps)

    return video_path, tracker_name, fps

def get_video_parameters(vs):
    video_params = OrderedDict()
    video_params['frames_count'] = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
    video_params['original_fps'] = vs.get(cv2.CAP_PROP_FPS)
    video_params['video_width']  = int(vs.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_params['video_height'] = int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return video_params

def consolidate_annotations():
    pass

def process_video(video_path, tracker_name, fps):
    
    try:
        video_stream = cv2.VideoCapture(video_path)   # Create Opencv's video stream object
    except:
        pass

    if not video_stream.isOpened(): 
        print ("Error: Could not open video file at -->",video_path)
        return
    else:
        video_params = get_video_parameters(video_stream)
        start_video(video_stream, video_params, tracker_name, fps)
        video_stream.release()    # release the file pointer
        cv2.destroyAllWindows()   # close all windows

def start_tracking(frame, tracker_name, tracking_algos):
    #tracker_list = [*tracking_algos]           ###################################################3
    #tracker_name = tracker_list[tracker_pos]   ###############################################
    trackers = cv2.MultiTracker_create()
    # select the bounding box of the object we want to track (make
    # sure you press ENTER or SPACE after selecting the ROI)
    # If you need to reselect the region, simply press “ESCAPE”.
    # OpenCV says press c to cancel objects selection process. It doesn't work. Press Escape to exit selection process
    print ('After selecting each bounding box, you need to click on "Enter" or "Space" button to finalize it') 
    print ('and start selecting a new bounding box. Once you are done with ALL bounding boxes selection,')
    print ('press "Esc" key to end ROI selection and start tracking.')
    print ('Also, if you need to reset bounding boxes for any reason, press "r" button.')
    box = cv2.selectROIs("frame", frame, fromCenter=False, showCrosshair=True)
    box = tuple(map(tuple, box))
    for bb in box:
        tracker = tracking_algos[tracker_name]()
        trackers.add(tracker, frame, bb)

    return trackers, box

def display_frame(vs, video_params, trackers, tracker_name, paused, flag='next', user=1):
    ret = None
    frame = None

    if flag == 'next':
        ret, frame = vs.read()  # vs.read method advances the current video position one frame forward

    if flag == 'prev':
        next_frame = vs.get(cv2.CAP_PROP_POS_FRAMES)
        previous_frame = next_frame - 2
        vs.set(cv2.CAP_PROP_POS_FRAMES, previous_frame)
        ret, frame = vs.read()

    if flag == 'cur':
        next_frame = vs.get(cv2.CAP_PROP_POS_FRAMES)
        current_frame = next_frame - 1
        vs.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = vs.read() 

    if not ret:
        return None, None

    (video_height, video_width) = frame.shape[:2]  ############

    next_frame_num = int(vs.get(cv2.CAP_PROP_POS_FRAMES))
    current_frame_num = next_frame_num - 1

    if current_frame_num == 0:
        paused = True
        display_text = 'Video paused: Press any key to start'
        cv2.putText(frame, display_text, (10, video_height - ((5 * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    text = "{}: {}".format('frame # ', current_frame_num)
    cv2.putText(frame, text, (10, video_height - ((3 * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    text = "{}: {}".format('Algo', tracker_name)
    cv2.putText(frame, text, (10, video_height - ((2 * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    (success, boxes) = trackers.update(frame)

    if success:    # if the tracking was a success
        for box in boxes:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow("frame", frame)    # show the output frame
    return frame, paused

def start_video(vs, video_params, tracker_name, fps):

    tracking_algos = OrderedDict()
    tracking_algos['csrt']       = cv2.TrackerCSRT_create         # Discriminative Correlation Filter (with Channel and Spatial Reliability)
    tracking_algos['kcf']        = cv2.TrackerKCF_create          # Kernelized Correlation Filters
    tracking_algos['boosting']   = cv2.TrackerBoosting_create
    tracking_algos['mil']        = cv2.TrackerMIL_create
    tracking_algos['tld']        = cv2.TrackerTLD_create
    tracking_algos['medianflow'] = cv2.TrackerMedianFlow_create
    tracking_algos['mosse']      = cv2.TrackerMOSSE_create        # Extremely fast but not as accurate as either KCF or CSRT
    tracker_list = [*tracking_algos]
    tracker_pos  = tracker_list.index(tracker_name)

    trackers = cv2.MultiTracker_create() 

    paused = True

    while vs.isOpened():
        try:
            frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused)    # grab the current frame
        except:
            print ('display_frame function excepted' )    # Only if NOT LAST frame
            break

        if paused == True:
            sleep_time = 0
        else:
            sleep_time = int(1000/fps)

        key = cv2.waitKey(sleep_time) & 0xFF

        if key == ord('q'):  # quit
            print('Exit by user')
            break

        elif key == ord('g'):  # Play at fps
            frame, paused = display_frame(vs, video_params, trackers, tracker_name, False)

        # if the 's' key is pressed, we will "select" a bounding boxes to track objects
        elif key == ord('s'):
            trackers, box = start_tracking(frame, tracker_name, tracking_algos)
            frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')
        
        elif key == ord('r'): # select the 'r' key to reset bounding box
            trackers.clear()
            trackers, box = start_tracking(frame, tracker_name, tracking_algos)
            frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')

        elif key == ord('t'):    # select next tracking algo
            if tracker_pos == len(tracker_list):
                tracker_pos = 0
            else:
                tracker_pos += 1
            tracker_name = tracker_list[tracker_pos]
            print (tracker_name, ' tracking algo selected')
            trackers, box = start_tracking(frame, tracker_name, tracking_algos)
            frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')

        elif key == ord('y'):    # select previous tracking algo
            if tracker_pos > 0:
                tracker_pos -= 1
            else:
                tracker_pos = len(tracker_list)
            tracker_name = tracker_list[tracker_pos]
            print (tracker_name, ' tracking algo selected')
            trackers, box = start_tracking(frame, tracker_name, tracking_algos)
            frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')

        elif key == ord('x'):
            paused = True
            print('Paused')
            while True:
                key2 = cv2.waitKey(1) or 0xff  # waiting for another key to be pressed
                cv2.imshow('frame', frame)  
                
                if key2 == ord('x'):   # pause pressed again
                    print('Resumed')
                    paused = False
                    break              # resume

                elif key2 == ord('q'):  # quit
                    print('Exit by user')
                    exit()

                elif key2 == ord('n'):  # Next frame
                    frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused)

                elif key2 == ord('p'):  # Previous frame
                    frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'prev')

                elif key2 == ord('s'):
                    trackers, box = start_tracking(frame, tracker_name, tracking_algos)
                    frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')

                elif key2 == ord('r'):
                    trackers.clear()
                    trackers, box = start_tracking(frame, tracker_name, tracking_algos)
                    frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')

                elif key2 == ord('t'):    # select next tracking algo
                    if tracker_pos == len(tracker_list):
                        tracker_pos = 0
                    else:
                        tracker_pos += 1
                    tracker_name = tracker_list[tracker_pos]
                    print (tracker_name, ' tracking algo selected')
                    trackers, box = start_tracking(frame, tracker_name, tracking_algos)
                    frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')

                elif key2 == ord('y'):    # select previous tracking algo
                    if tracker_pos > 0:
                        tracker_pos -= 1
                    else:
                        tracker_pos = len(tracker_list)
                    tracker_name = tracker_list[tracker_pos]
                    print (tracker_name, ' tracking algo selected')
                    trackers, box = start_tracking(frame, tracker_name, tracking_algos)
                    frame, paused = display_frame(vs, video_params, trackers, tracker_name, paused, 'cur')

                elif key2 == ord('+'):
                    key3 = cv2.waitKey(1) or 0xff  # waiting for another key to be pressed
                    print ('key3: ', key3)
                    cv2.imshow('frame', frame) 
                    pass

def create_folder(video_path):
    parent_folder = os.path.dirname(video_path)    # result is '' for './' 
    base = os.path.basename(video_path)
    new_folder = os.path.join(parent_folder,os.path.splitext(base)[0])

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
        print ('Created new folder for saving video annotations: ' , new_folder)
    else:
        print (new_folder, ' folder already exists. Video annotations will be saved here.')

def main():
    video_path, tracker_name,fps = parse_arguments()
    create_folder(video_path)
    process_video(video_path, tracker_name, fps)

if __name__ == "__main__":
    main()

# 2do:
# Show the objects already tagged
# user tagged = blue color
# Algo tagged = yellow color
# Tagging Consoliation script

# Display algo name only if tracking is on 
# Display when successfully tracked
# Logging
# Log to frame
# create folder and log file

''' 
cv2.set(CAP_PROP_POS_FRAMES) is known to not seek the specified frame accurately. 
This is perhaps because it seeks to the nearest keyframe. This means there might be 
repetition of a couple of frames at points where the video is fragmented. 
So it is not advisable to adopt this method for frame-critical use cases.

Keys->
    s-> region of intrest selector
    n-> next frame (first pause then use)
    p-> prev frame (first pause then use)
    q-> quit
    g-> play video at normal speed
    x-> pause/resume video
    t-> next tracker algo selector
    y-> previous tracker algo selector

Command to Run app ->

    python object_tracker.py --video [path/to/video] --tracker [tracker type example:csrt] --slow [time in sec to slow down video]

Example Command ->

    python object_tracker.py --video us_bp.mp4 --tracker csrt --slow 1

'''


