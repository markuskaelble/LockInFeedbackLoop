# LockInFeedbackLoop

For impleminting the Loop just add the feedback.py file to a project, import the File to the code via import feedback.py and call the Feedback Class:

FeedbackLoop("dev1492", "GPIB0::28", 1e6 )
FeedbackLoop("LockIn", "SMIQ", start_frequency)

Required packeges:
- numpy 
- zhinst 
- pyvisa 

For more Information about the LockIn API visit: https://docs.zhinst.com/labone_api/index.html

