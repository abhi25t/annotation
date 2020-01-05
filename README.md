# Annotation

When app starts: <br> 
press "**g**" to start video at normal speed <br>
Or press "**x**" for pausing video. Some functions work only in pause mode.<br><br>

**Key Functions -->**<br> 
**z** : Region of intrest selector <br> 
**Esc** : Finalize selection <br> 
**r** : Reset region of intrest selector <br> 
**q** : Quit app. Activate terminal window for further dialogue <br>
**t** : Next tracker algo selector <br> 
**y** : Previous tracker algo selector<br>

**x** : Pause video <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; Below keys work only in pause mode.<br>
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **n** : Display next frame <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **p** : Display prev frame <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **+** : Add a bounding box <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **-** : Remove a bounding box. Activate terminal window to input bounding box number <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **m** : Move a bounding box. Activate terminal window to input bounding box number. Press "0" when done with moving <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **s** : Move selected bounding box down by one pixel <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **a** : Move selected bounding box left by one pixel <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **d** : Move selected bounding box right by one pixel <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **w** : Move selected bounding box up by one pixel <br> 
&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; **0** : When done with moving, press "0" to deactivate moving mode. <br> 


**Command to Run app ->** <br>

> python annotate.py --video [path/to/video] --tracker [tracker algorithm] --fps [frames per sec] <br>

tracker (default = csrt) & fps (default = 10) are optional.<br>

**Example Command ->**<br>

> python annotate.py --video us_bp.mp4 --tracker csrt --fps 15
