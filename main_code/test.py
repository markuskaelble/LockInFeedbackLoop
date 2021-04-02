import pyvisa as visa
import numpy
#import logging
import time

# GPIB-USB-HS 'GPIB0'
# SMIQ 'GPIB0::14::INSTR'

from hardware.microwave_sources import SMIQ
class FeedbackLoop( SMIQ ):
    def __init__(self,signal_input, signal_output):
        SMIQ()
        self.signal_input = signal_input
        self.signal_output = signal_output
        self.visa_address = signal_output
        
        SMIQ.setFrequency(self, 2837176000)
        
    
   

if __name__ == "__main__":
    FeedbackLoop("dev1492", "GPIB0::28")