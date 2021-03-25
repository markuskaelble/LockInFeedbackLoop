""" Legend:
incomingData [Voltage] --> Used by ZI API
outgoingData [Frequency] --> Used by ZI API 


All Names are relativ to the programm.
"""
# import of existing python packeges
import numpy as np
import zhinst 

# import of self made funktions, alias the other files
#import dummy 


# definition of the main Function
class FeedbackLoop():

    def __init__(self,signal_input, signal_output):
        self.signal_input = signal_input
        self.signal_output = signal_output
        self._run()
       



    def _run(self): #contains the main loop
       
       
       """ Definition of used variables """
        I=0
        self.outgoingData = 0.0 




        def _calculation(self,incomingData): #modifys the freqeuncy
            self.outgoingData = self.incomingData * 2
            return self.outgoingData

        def _readData(self, signal_input): #readsThe Incoming data form  signal_input. Incoming data has to be called form the API, returns the voltage 
            self.incomingData = 1.0
            return self.incomingData

        def _writeData(self, signal_output, outgoingData): #writes the new frequency to the signal_output. OutgoingData contains the modified frequency 
            return print(outgoingData)
        
    
        while True:
            try:
                #print("Running")
                
                x=_calculation(self, _readData(self, "lol"))
                
                print(x)
                I+=1
            finally:
                
                if I==1000:
                    break
                
        print("Done!")


    def _calculation(self,incomingData): #modifys the freqeuncy
        self.incomingData= self.outgoingData * 2
        return 

    def _readData(self, signal_input): #readsThe Incoming data form  signal_input. Incoming data has to be called form the API, returns the voltage 
        self.incomingData = 1.0 
        return self.incomingData

    def _writeData(self, signal_output, outgoingData): #writes the new frequency to the signal_output. OutgoingData contains the modified frequency 
        return print(outgoingData)





if __name__ == "__main__":  # runs the main() funktion, when file is called
    FeedbackLoop("Dev1/AI0", "Dev2/AO0")