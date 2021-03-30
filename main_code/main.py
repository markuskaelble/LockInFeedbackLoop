"""=======================================================================================================================
Some Random Notes:

incomingData [Voltage] --> Used by ZI API
outgoingData [Frequency] --> Used by ZI API 


All Names are relativ to the programm.


While testing keep the power for the SIMQ at -40


TO-Do:
- check if LockIn data can be received and bug fix it. 
- check if SMIQ can be controlled by the API and bug fix it 
- implement the actual modification of the frequency in dependency of the LockIn
- delete all lines with testing purposes
======================================================================================================================="""



"""-----------------------------------------------------------------------------------------------------------------------
import of existing python packages and user-written ones.
-----------------------------------------------------------------------------------------------------------------------"""

import numpy as np
import zhinst 
import daemon
import pyvisa as visa

from hardware.microwave_sources import SMIQ
from hardware.lockin_sources import *


class FeedbackLoop( SMIQ ):

    def __init__(self,signal_input, signal_output):
        SMIQ()
        self.signal_input = signal_input
        self.signal_output = signal_output
        self.visa_address = signal_output
        
       # self.instr = visa.instrument(self.visa_address)
        
        self._run() # daemon hast to be implemented here
       
    def _run(self): #contains the main loop
        
        """ variable decleration """
        self.outgoingData = 0.0     


        # Scope setup. In the final version this should be done in  main programm,  not inside the Loop Class
        #setup_scope(device_id= self.signal_output)

        ############################################################################################################################
        
        def _readData(self, signal_input): 
            """-----------------------------------------------------------------------------------------------------------------------
            The actual reading function is defined inside scope_sources.py, here they are just called. 
            Later implementation of the actual function. 

            The processing of the result is a result of the assumption for a certain measurement output. 
            The output should be a dict with one entry inside.  
            -----------------------------------------------------------------------------------------------------------------------"""
            
            #result = get_scope_records( self.signal_input, daq, scopeModule, min_num_records)   
            result = {  1: [1,2,3,4,5,6]} # dict for testing porposes 
            
            data = list(result.values())
            self.incomingData = np.average(np.array(data))
            return self.incomingData
        
        
        
        def _calculation(self,incomingData): 
            """-----------------------------------------------------------------------------------------------------------------------
            here the actual calculation will be done.  
            For testing purposes, there is none calculation for now.   
            -----------------------------------------------------------------------------------------------------------------------"""
            self.outgoingData = self.incomingData 
            return self.outgoingData



        def _writeData(self, signal_output, outgoingData): 
            """-----------------------------------------------------------------------------------------------------------------------
            Calls for the SMIQ API to write the new frequency.
            -----------------------------------------------------------------------------------------------------------------------"""
            #SMIQ.setFrequency(self, outgoingData)
            return print(outgoingData) 

        ############################################################################################################################

        # the actuall Loop
        i = 1
        while True:
            try:
                _writeData(self,"lol", _calculation(self, _readData(self, "lol")))
            finally:
                
                i+=1 
                if i == 100:
                    break
        print("Done!") # print messages and if loop will be removed later.  Only for testing purposes


"""-----------------------------------------------------------------------------------------------------------------------
Every time main.py is called this function will execute the class above. The call for the class should be implemented in the main program. 
Here it just added for testing purposes.
-----------------------------------------------------------------------------------------------------------------------"""
if __name__ == "__main__":
    FeedbackLoop("Dev1/AI0", "GPIB0::28")