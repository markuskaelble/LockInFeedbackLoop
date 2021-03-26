# LockInFeedbackLoop


FeedbackLoop for the adjustment for the output frequency for a SMIQ generator, according to the LockIn measurement of a Zurich Instrument LockIn 50 MHz.
The file contains the Loop itself. By calling the class the daemon starts and adjusts the frequency.
Call with: FeedbackLoop(LockIn_channel , SMIQ_channel)


Skript can be executed as Docker image with "python main_code/main.py".
