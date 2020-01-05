# Annotation

When app starts: <br> 
press "**g**" to start video at normal speed <br>
Or press "**x**" for pausing video. Some functions work only in pause mode.<br><br>

**Key Functions -->**<br> 
**s** : Region of intrest selector <br> 
**Esc** : Finalize selection <br> 
**r** : Reset region of intrest selector <br> 
**q** : Quit app. Activate terminal window for further dialogue <br>
**t** : Next tracker algo selector <br> 
**y** : Previous tracker algo selector<br>

**x** : Pause video <br> 
Below keys work only in pause mode.<br>
**n** : Display next frame <br> 
**p** : Display prev frame <br> 
**+** : Add a bounding box <br> 
**-** : Remove a bounding box. Activate terminal window to input bounding box number <br> 
**m** : Move a bounding box. Activate terminal window to input bounding box number <br> 
**s** : Region of intrest selector <br> 


**Command to Run app ->** <br>

> python object_tracker.py --video [path/to/video] --tracker [tracker algorithm] --fps [frames per sec] <br>

tracker & fps are optional <br>

**Example Command ->**<br>

> python object_tracker.py --video us_bp.mp4 --tracker csrt --fps 15
