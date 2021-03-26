""" Some Information:
incomingData [Voltage] --> Used by ZI API
outgoingData [Frequency] --> Used by ZI API 


All Names are relativ to the programm.


While testing keep the power for the SIMQ at -40
"""
# import of existing python packeges
import numpy as np
import zhinst 
import daemon
import pyvisa as visa


from hardware.microwave_sources import SMIQ


# definition of the main Function
class FeedbackLoop( SMIQ ):

    def __init__(self,signal_input, signal_output):
        SMIQ()
        self.signal_input = signal_input
        self.signal_output = signal_output
        self.visa_address = signal_output
        
       # self.instr = visa.instrument(self.visa_address)
        
        daemon.DaemonContext(self._run())
       
    def _run(self): #contains the main loop
        
        I=0                         # Definition of used variables 
        self.outgoingData = 0.0     



        ############################################################################################################################
        
        
        def _readData(self, signal_input): #readsThe Incoming data form  signal_input. Incoming data has to be called form the API, returns the voltage 
            self.incomingData = 100.0
            return self.incomingData
        
        
        
        def _calculation(self,incomingData): #modifys the freqeuncy 
            """
            pleas add a fancy equation here
            """
            self.outgoingData = self.incomingData *2 
            return self.outgoingData



        def _writeData(self, signal_output, outgoingData): #writes the new frequency to the signal_output. OutgoingData contains the modified frequency 
            SMIQ.setFrequency(self, outgoingData)
            return print(outgoingData) 

        ############################################################################################################################

        while True:
            try:
                _writeData(self,"lol", _calculation(self, _readData(self, "lol")))
                

            finally:
                I+=1
                if I==10:
                    break
                
        print("Done!")





if __name__ == "__main__":  # runs the main() funktion, when file is called
    
    FeedbackLoop("Dev1/AI0", "GPIB0::28")