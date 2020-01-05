import cv2
import argparse, os, sys, json
import inspect
from datetime     import datetime
from collections  import OrderedDict
from functools    import partial

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
    video_params = {}    #OrderedDict()
    video_params['frames_count'] = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
    video_params['original_fps'] = vs.get(cv2.CAP_PROP_FPS)
    video_params['video_width']  = int(vs.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_params['video_height'] = int(vs.get(cv2.CAP_PROP_FRAME_HEIGHT))

    return video_params

def output_annotations(new_annotations_file, data):

    logging_data = {} 

    frame_num = int(data['frameNo'])
    user      = data['user']

    logging_data[frame_num] = {}
    logging_data[frame_num]['tracker'       ] = 'human' if user==1 else data['tracker']
    logging_data[frame_num]['bounding_boxes'] = str(data['bounding_boxes'])

    new_annotations_file.write(json.dumps(logging_data))
    new_annotations_file.write('\n')

def update_annotation_file(new_annotations_path, old_annotations_path):
    '''
    I can't do a simple append to old file because, I need to overwrite duplicates (which are actually updates) from old files
    '''
    annotations = OrderedDict()     # use OrderedDict here for using sorting

    #if old_annotations_path is not None:
    if os.path.isfile(old_annotations_path):
        old_input_file = open(old_annotations_path, 'r')
        for line in old_input_file:
            json_decode = json.loads(line)
            for item in json_decode:
                annotations[item] = json_decode[item]
        old_input_file.close()

    new_input_file = open(new_annotations_path, 'r')
    for line in new_input_file:
        json_decode = json.loads(line)
        for item in json_decode:
            annotations[item] = json_decode[item]
    new_input_file.close()

    # Write fresh
    new_annotations_file = open(old_annotations_path, 'w')
    for item in annotations:
        new_annotations_file.write('{"' + item + '":' + json.dumps(annotations[item])    + '}')
        new_annotations_file.write('\n')
    new_annotations_file.close()       

    # Don't update if human. 
    # Well what if human really wants himself to be overwritten.... Think about asking for input

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
    boxes = cv2.selectROIs("frame", frame, fromCenter=False, showCrosshair=True)
    boxes = tuple(map(tuple, boxes))
    for bb in boxes:
        tracker = tracking_algos[tracker_name]()
        trackers.add(tracker, frame, bb)

    return trackers, list(boxes)

def display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, flag='next', user=False):
    ret = None
    frame = None
    boxes_with_int_coords = []

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
    cv2.putText(frame, text, (10, video_height - 80 ), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    (success, boxes) = trackers.update(frame)

    if tracking_on == True:     
        text = "{}: {}".format('Algo', tracker_name)
        cv2.putText(frame, text, (10, video_height - 60 ), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
  
        for box in boxes:
            box_int = [int(v) for v in box]
            (x, y, w, h) = box_int
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            boxes_with_int_coords.append(box_int)

        display_bounding_box_num(frame, boxes_with_int_coords, (0, 255, 0) )
        #print ('------>' , boxes_with_int_coords) 
        output_annotations(new_annotations_file, {
                "bounding_boxes":boxes_with_int_coords,
                "tracker"       : tracker_name,
                "frameNo"       : vs.get(cv2.CAP_PROP_POS_FRAMES) - 1,
                "user"          : 1 if user else 0   }   )
    else:
        tracker_used, old_bounding_boxes = get_boxes_for_frame(current_frame_num, old_annotations)

        if tracker_used is not None:
            if tracker_used == 'human' :
                color = (208, 224, 64)   # turquoise
            else:
                color = (0, 165, 255)    # orange

            text = "{}: {}".format('Algo', tracker_used)
            cv2.putText(frame, text, (10, video_height - 60 ), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
 
            old_bounding_boxes = eval(old_bounding_boxes)
            display_bounding_box_num(frame, old_bounding_boxes, color)
            for box in old_bounding_boxes:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

    cv2.setTrackbarPos('Slider:', 'frame', current_frame_num)
    cv2.imshow("frame", frame)    # show the output frame
    return frame, paused, boxes_with_int_coords

def display_bounding_box_num(frame, boxes, color):
    bb_num = 0
    for box in boxes:
        (x, y, w, h) = [int(v) for v in box]
        x += int(w/2) 
        y += int(h/2) + 5
        cv2.putText(frame, str(bb_num), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        bb_num +=1

def exit_program( vs, tracking_on, new_annotations_file, new_annotations_path, old_annotations_path ):
    vs.release()    # release the file pointer
    cv2.destroyAllWindows()   # close all windows            
    new_annotations_file.close()
    print('Exit by user')
    if tracking_on == True:
        merger = input("Shall we update Consolidated file with current session annotations ? (y/n): ") 
        if merger == 'y':
            update_annotation_file(new_annotations_path, old_annotations_path)
        else:
            print ('No. It was not useful !')
    else:
        print ('No new annotations in this session to update.')

    exit()

def get_boxes_for_frame(frame_num, old_annotations):

    try:
        frame_annotations = old_annotations[str(frame_num)]
        tracker = frame_annotations['tracker']
        bounding_boxes = frame_annotations['bounding_boxes']

        return tracker, bounding_boxes
    except:
        return None, None 

def trackbar_change(trackbar_value, vs_):
    called_by = inspect.stack()[1].function
    if called_by == 'process_video':
        vs_.set(cv2.CAP_PROP_POS_FRAMES, trackbar_value-1)
        ret, frame_ = vs_.read()
        cv2.imshow("frame", frame_ ) 
        cv2.waitKey(1)

def process_video(video_path, tracker_name, fps):
    try:
        vs = cv2.VideoCapture(video_path)   # Create Opencv's video stream object
    except:
        pass

    if not vs.isOpened(): 
        print ("Error: Could not open video file at -->",video_path)
        exit()
   
    old_annotations, old_annotations_path = get_previous_annotations(video_path)

    new_annotations_path = create_folder_and_file(video_path)         
    new_annotations_file = open(new_annotations_path, 'w')

    trackers     = cv2.MultiTracker_create() 
    video_params = get_video_parameters(vs)
    paused       = True
    tracking_on  = False

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

    length = video_params['frames_count'] - 1
    cv2.namedWindow('frame')
    cv2.createTrackbar( 'Slider:', 'frame', 0, length, partial(trackbar_change, vs_ = vs)  )

    while vs.isOpened():

        frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on)    # grab the current frame

        if paused == True:
            sleep_time = 0
        else:
            sleep_time = int(1000/fps)

        key = cv2.waitKey(sleep_time) & 0xFF

        if key == ord('q'):  # quit
            exit_program( vs, tracking_on, new_annotations_file, new_annotations_path, old_annotations_path )

        elif key == ord('g'):  # Play at fps
            frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, False, new_annotations_file, old_annotations, tracking_on)

        # if the 'z' key is pressed, we will "select" a bounding boxes to track objects
        elif key == ord('z'):
            trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
            tracking_on = True
            frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user = True)
        
        elif key == ord('r'): # select the 'r' key to reset bounding boxes
            trackers.clear()
            trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
            tracking_on = True
            frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user = True)

        elif key == ord('t'):    # select next tracking algo
            if tracker_pos == len(tracker_list):
                tracker_pos = 0
            else:
                tracker_pos += 1
            tracker_name = tracker_list[tracker_pos]
            print (tracker_name, ' tracking algo selected')
            trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
            tracking_on = True
            frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)

        elif key == ord('y'):    # select previous tracking algo
            if tracker_pos > 0:
                tracker_pos -= 1
            else:
                tracker_pos = len(tracker_list)
            tracker_name = tracker_list[tracker_pos]
            print (tracker_name, ' tracking algo selected')
            trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
            tracking_on   = True
            frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)

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
                    exit_program( vs, tracking_on, new_annotations_file, new_annotations_path, old_annotations_path )

                elif key2 == ord('n'):  # Next frame
                    frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on)
                    

                elif key2 == ord('p'):  # Previous frame
                    frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'prev')

                elif key2 == ord('z'):
                    tracking_on=True
                    trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
                    frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)

                elif key2 == ord('r'):
                    trackers.clear()
                    trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
                    tracking_on = True
                    frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)

                elif key2 == ord('t'):    # select next tracking algo
                    if tracker_pos == len(tracker_list):
                        tracker_pos = 0
                    else:
                        tracker_pos += 1
                        
                    tracker_name = tracker_list[tracker_pos]
                    print (tracker_name, ' tracking algo selected')
                    trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
                    tracking_on = True
                    frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)

                elif key2 == ord('y'):    # select previous tracking algo
                    if tracker_pos > 0:
                        tracker_pos -= 1
                    else:
                        tracker_pos = len(tracker_list)

                    tracker_name = tracker_list[tracker_pos]
                    print (tracker_name, ' tracking algo selected')
                    trackers, boxes = start_tracking(frame, tracker_name, tracking_algos)
                    tracking_on = True
                    frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)

                elif key2 == ord('+'):
                    if tracking_on == True:
                        print ('Add a bounding box ...')
                        bb = cv2.selectROI("frame", frame, fromCenter=False, showCrosshair=True)
                        tracker = tracking_algos[tracker_name]()
                        trackers.add(tracker, frame, bb)
                        frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)
                    else:
                        print ('Tracking not started yet. Press "s" to start tracking')

                elif key2 == ord('-'):
                    if tracking_on == True:
                        box_to_del = input("Which box do you want to delete ?: ")
                        boxes.pop(int(box_to_del))
                        print ('Deleted box # ' , box_to_del )
                        # Restart tracker with remaining boxes 
                        frame, paused, boxes, trackers = restart_tracking_new_boxes(boxes, trackers, tracking_algos, tracker_name, frame, vs, video_params,paused, new_annotations_file, old_annotations, tracking_on)  
                    else:
                        print ('Tracking not started yet. Press "s" to start tracking')

                elif key2 == ord('m'):
                    if tracking_on == True:
                        box_to_move = input("Which box do you want to move ?: ")
                        print('Press "0" when done moving')
                        [x, y, w, h] = boxes[int(box_to_move)]

                        key3 = cv2.waitKey(1) or 0xff  # waiting for another key to be pressed
                        cv2.imshow('frame', frame) 

                        while True:
                            key3 = cv2.waitKey(1) or 0xff 
                            if key3 == ord('s'):   # down
                                y += 1
                                boxes.pop(int(box_to_move))
                                boxes.insert( int(box_to_move) , [x, y, w, h] )
                                frame, paused, boxes, trackers = restart_tracking_new_boxes(boxes, trackers, tracking_algos, tracker_name, frame, vs, video_params,paused, new_annotations_file, old_annotations, tracking_on)  
                                print ('Moved bounding box # ', box_to_move, ' down by 1 pixel')
                            elif key3 == ord('a'):   # left
                                x -= 1
                                boxes.pop(int(box_to_move))
                                boxes.insert( int(box_to_move) , [x, y, w, h] )
                                frame, paused, boxes, trackers = restart_tracking_new_boxes(boxes, trackers, tracking_algos, tracker_name, frame, vs, video_params,paused, new_annotations_file, old_annotations, tracking_on)  
                                print ('Moved bounding box # ', box_to_move, ' left by 1 pixel')
                            elif key3 == ord('d'):   # right
                                x += 1
                                boxes.pop(int(box_to_move))
                                boxes.insert( int(box_to_move) , [x, y, w, h] )
                                frame, paused, boxes, trackers = restart_tracking_new_boxes(boxes, trackers, tracking_algos, tracker_name, frame, vs, video_params,paused, new_annotations_file, old_annotations, tracking_on)  
                                print ('Moved bounding box # ', box_to_move, ' right by 1 pixel')
                            elif key3 == ord('w'):   # up
                                y -= 1
                                boxes.pop(int(box_to_move))
                                boxes.insert( int(box_to_move) , [x, y, w, h] )
                                frame, paused, boxes, trackers = restart_tracking_new_boxes(boxes, trackers, tracking_algos, tracker_name, frame, vs, video_params,paused, new_annotations_file, old_annotations, tracking_on)  
                                print ('Moved bounding box # ', box_to_move, ' up by 1 pixel')
                            elif key3 == ord('q'):   # quit
                                exit_program( vs, tracking_on, new_annotations_file, new_annotations_path, old_annotations_path )
                            elif key3 == ord('0'):
                                break
                    else:
                        print ('Tracking not started yet. Press "s" to start tracking')

    vs.release()    # release the file pointer
    cv2.destroyAllWindows()   # close all windows

def restart_tracking_new_boxes(boxes, trackers, tracking_algos, tracker_name, frame, vs, video_params,paused, new_annotations_file, old_annotations, tracking_on):
    boxes = [tuple(box) for box in boxes]
    boxes = tuple(boxes)
    trackers.clear()
    trackers = cv2.MultiTracker_create()
    for bb in boxes:
        tracker = tracking_algos[tracker_name]()
        trackers.add(tracker, frame, bb)                        
    frame, paused, boxes = display_frame(vs, video_params, trackers, tracker_name, paused, new_annotations_file, old_annotations, tracking_on, 'cur', user=True)

    return frame, paused, boxes, trackers

def create_folder_and_file(video_path):
    parent_folder = os.path.dirname(video_path)    # result is '' for './' 
    base = os.path.basename(video_path)
    new_folder = os.path.join(parent_folder,os.path.splitext(base)[0])

    if not os.path.exists(new_folder):
        os.makedirs(new_folder)
        print ('Created new folder for saving video annotations: ' , new_folder)
    else:
        print (new_folder, ' folder already exists. Video annotations will be referred to here.')

    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    
    new_annotations_path = os.path.join(new_folder, current_time + '.txt')

    return new_annotations_path

def get_previous_annotations(video_path):

    parent_folder        = os.path.dirname(video_path)    # result is '' for './' 
    base_primary         = os.path.splitext(os.path.basename(video_path))[0]  
    new_folder           = os.path.join(parent_folder, base_primary)
    old_annotations_path = os.path.join(new_folder,base_primary + '.txt') 

    if os.path.isfile(old_annotations_path):
        print ("Consolidated annotations file found :" , old_annotations_path)
        old_annotations={}
        input_file = open(old_annotations_path, 'r')
        for line in input_file:
            json_decode = json.loads(line)
            for item in json_decode:
                old_annotations[item] = json_decode[item]
        input_file.close()
        #print (old_annotations['9'])
        return old_annotations, old_annotations_path

    else:
        print ("Consolidated annotations file not found.  Will create new : " , old_annotations_path)
        return None, old_annotations_path

def main():
    video_path, tracker_name,fps = parse_arguments()
    process_video(video_path, tracker_name, fps)

if __name__ == "__main__":
    main()

''' 
When app starts:
press "g" to start video at normal speed
Or press "x" for pausing video. Some functions work only in pause mode. 

Key Functions -->
z : Region of intrest selector
Esc : Finalize selection
r : Reset region of intrest selector
q : Quit app. Activate terminal window for further dialogue
t : Next tracker algo selector
y : Previous tracker algo selector

x : Pause video
          Below keys work only in pause mode.
          n : Display next frame
          p : Display prev frame
          + : Add a bounding box
          - : Remove a bounding box. Activate terminal window to input bounding box number
          m : Move a bounding box. Activate terminal window to input bounding box number. Press "0" when done with moving
                    s : Move selected bounding box down by one pixel
                    a : Move selected bounding box left by one pixel
                    d : Move selected bounding box right by one pixel
                    w : Move selected bounding box up by one pixel
                    0 : When done with moving, press "0" to deactivate moving mode. 

Command to Run app ->

    python object_tracker.py --video [path/to/video] --tracker [tracker algorithm] --fps [frames per sec]

Example Command ->

    python object_tracker.py --video us_bp.mp4 --tracker csrt --fps 15

Tracking algo explanations:
https://www.learnopencv.com/object-tracking-using-opencv-cpp-python/

cv2.set(CAP_PROP_POS_FRAMES) is known to not seek the specified frame accurately. 
This is perhaps because it seeks to the nearest keyframe. This means there might be 
repetition of a couple of frames at points where the video is fragmented. 
So it is not advisable to adopt this method for frame-critical use cases.
'''


