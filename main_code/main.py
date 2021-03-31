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
from numpy import array
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
        """-----------------------------------------------------------------------------------------------------------------------
        Settings for the LockIn well be outsourced later to lockin_sources
        -----------------------------------------------------------------------------------------------------------------------"""
        
        device_id = self.signal_input
        scope_inputselect=0
        sigouts_amplitude=0.1
        module_averaging_weight=1
        module_historylength=20
        min_num_records=1
        apilevel_example = 1

        err_msg = "This example only supports HF2 Instruments."
        
        """================================API configurations================================"""

     
        # Call a zhinst utility function that returns:
        # - an API session `daq` in order to communicate with devices via the data server.
        # - the device ID string that specifies the device branch in the server's node hierarchy.
        # - the device's discovery properties.

        (daq, device, props) = zhinst.utils.create_api_session(device_id, apilevel_example, required_devtype="HF2", required_err_msg=err_msg)
        zhinst.utils.api_server_version_check(daq)
        daq.setDebugLevel(3) # Enable the API's log
        zhinst.utils.disable_everything(daq, device)  # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...

        """================================Experiment configurations================================"""
        
        scope_settings = [
            ["/%s/scopes/0/channel" % (device), scope_inputselect],
            # Enable bandwidth limiting: avoid antialiasing effects due to
            # sub-sampling when the scope sample rate is less than the input
            # channel's sample rate.
            ["/%s/scopes/0/bwlimit" % (device), 1],
            # Set the sampling rate.
            ["/%s/scopes/0/time" % (device), 0],
            # Enable the scope
            ["/%s/scopes/0/enable" % device, 1],
        ]
        daq.set(scope_settings)
    
        # Perform a global synchronisation between the device and the data server:
        # Ensure that the settings have taken effect on the device before acquiring data.
        daq.sync()
    
        # Now initialize and configure the Scope Module.
        scopeModule = daq.scopeModule()
        # 'mode' : Scope data processing mode.
        # 0 - Pass through scope segments assembled, returned unprocessed, non-interleaved.
        # 1 - Moving average, scope recording assembled, scaling applied, averaged, if averaging is enabled.
        # 2 - Not yet supported.
        # 3 - As for mode 1, except an FFT is applied to every segment of the scope recording.
        scopeModule.set("mode", 1)
        # 'averager/weight' : Averager behaviour.
        #   weight=1 - don't average.
        #   weight>1 - average the scope record shots using an exponentially weighted moving average.
        scopeModule.set("averager/weight", module_averaging_weight)
        # 'historylength' : The number of scope records to keep in the Scope Module's memory, when more records
        #   arrive in the Module from the device the oldest records are overwritten.
        scopeModule.set("historylength", module_historylength)
    
        scope_channel_lookup = {0: "sigin0", 1: "sigin1", 2: "sigout0", 3: "sigout1"}
        scope_channel = scope_channel_lookup[scope_inputselect]
        
        if scope_channel == "sigin0":
            externalscaling = daq.getDouble(f"/{device}/sigins/0/range")
        elif scope_channel == "sigin1":
            externalscaling = daq.getDouble(f"/{device}/sigins/1/range")
        elif scope_channel == "sigout0":
            externalscaling = daq.getDouble(f"/{device}/sigouts/0/range")
        elif scope_channel == "sigout1":
            externalscaling = daq.getDouble(f"/{device}/sigouts/1/range")
        
        scopeModule.set("externalscaling", externalscaling)
        
        # Subscribe to the scope's data in the module.
        wave_nodepath = f"/{device}/scopes/0/wave"
        scopeModule.subscribe(wave_nodepath)
        
        """-----------------------------------------------------------------------------------------------------------------------
        -----------------------------------------------------------------------------------------------------------------------"""

        # Scope setup. In the final version this should be done in  main programm,  not inside the Loop Class
        #setup_scope(self.signal_input)

        ############################################################################################################################
        
        def _readData(self, signal_input): 
            """-----------------------------------------------------------------------------------------------------------------------
            The actual reading function is defined inside scope_sources.py, here they are just called. 
            Later implementation of the actual function. 

            The processing of the result is a result of the assumption for a certain measurement output. 
            The output should be a dict with one entry inside.  
            -----------------------------------------------------------------------------------------------------------------------"""
            
            result = get_scope_records( self.signal_input, daq, scopeModule, min_num_records)   
            
            #result = {  'wave' : array([[1740, 1778, 1736, 1712, 1768, 1760]])} # dict for testing porposes 
            #print(result.keys())
            #self.incomingData = result.get('dev1492', {}).get('scopes', {}).get('0',{}).get('wave')
            self.incomingData = (result ['dev1492']['scopes']['0']['wave']['header'])
            #data = list(result.values())
            #self.incomingData = np.average(np.array(data))
            
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
        i = 0
        while True:
            try:
                _writeData(self,"lol", _calculation(self, _readData(self, "lol")))
                
            finally:
                
                i+=1 
                if i == 1:
                    break
        print("Done!") # print messages and if loop will be removed later.  Only for testing purposes


"""-----------------------------------------------------------------------------------------------------------------------
Every time main.py is called this function will execute the class above. The call for the class should be implemented in the main program. 
Here it just added for testing purposes.
-----------------------------------------------------------------------------------------------------------------------"""
if __name__ == "__main__":
    FeedbackLoop("dev1492", "GPIB0::28")