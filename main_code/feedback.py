"""-----------------------------------------------------------------------------------------------------------------------
import of existing python packages and user-written ones.
-----------------------------------------------------------------------------------------------------------------------"""
import numpy as np
from numpy import array, int64, uint64, uint32, int32, float32, int8, average
import zhinst
import zhinst.utils
import pyvisa as visa


import time
import warnings
import logging





class SMIQ():
    """Provides control of SMIQ family microwave sources from Rhode und Schwarz with GPIB via visa."""
    _output_threshold = -90.0
    
    def __init__(self, visa_address='GPIB0::28'):
        self.visa_address = visa_address
        
    def _write(self, string):
        try: # if the connection is already open, this will work
            self.instr.write(string)
        except: # else we attempt to open the connection and try again
            try: # silently ignore possible exceptions raised by del
                del self.instr
            except Exception:
                pass
            if hasattr(visa,"instrument"):
                self.instr = visa.instrument(self.visa_address)
            else:
                self.instr = visa.ResourceManager().open_resource(self.visa_address)
            self.instr.write(string)
        
    def _ask(self, str):
        try:
            val = self.instr.ask(str)
        except:
            self.instr = visa.instrument(self.visa_address)
            val = self.instr.ask(str)
        return val

    def getPower(self):
        return float(self._ask(':POW?'))

    def setPower(self, power):
        if power is None or power < self._output_threshold:
            logging.getLogger().debug('SMIQ at '+str(self.visa_address)+' turning off.')
            self._write(':FREQ:MODE CW')
            self._write(':OUTP OFF')
            return
        logging.getLogger().debug('SMIQ at '+str(self.visa_address)+' setting power to '+str(power))
        self._write(':FREQ:MODE CW')
        self._write(':POW %f' % float(power))
        self._write(':OUTP ON')

    def getFrequency(self):
        return float(self._ask(':FREQ?'))

    def setFrequency(self, frequency):
        self._write(':FREQ:MODE CW')
        self._write(':FREQ %f' % frequency)

    def setOutput(self, power, frequency):
        self.setPower(power)
        self.setFrequency(frequency)

    def initSweep(self, frequency, power):
        if len(frequency) != len(power):
            raise ValueError('Length mismatch between list of frequencies and list of powers.')
        self._write(':FREQ:MODE CW')
        self._write(':LIST:DEL:ALL')
        self._write('*WAI')
        self._write(":LIST:SEL 'ODMR'")
        FreqString = ''
        for f in frequency[:-1]:
            FreqString += ' %f,' % f
        FreqString += ' %f' % frequency[-1]
        self._write(':LIST:FREQ' + FreqString)
        self._write('*WAI')
        PowerString = ''
        for p in power[:-1]:
            PowerString += ' %f,' % p
        PowerString += ' %f' % power[-1]
        self._write(':LIST:POW'  +  PowerString)
        self._write(':LIST:LEAR')
        self._write(':TRIG1:LIST:SOUR EXT')
        # we switch frequency on negative edge. Thus, the first square pulse of the train
        # is first used for gated count and then the frequency is increased. In this way
        # the first frequency in the list will correspond exactly to the first acquired count. 
        self._write(':TRIG1:SLOP NEG') 
        self._write(':LIST:MODE STEP')
        self._write(':FREQ:MODE LIST')
        self._write('*WAI')
        N = int(numpy.round(float(self._ask(':LIST:FREQ:POIN?'))))
        if N != len(frequency):
            raise RuntimeError, 'Error in SMIQ with List Mode'

    def resetListPos(self):
        self._write(':ABOR:LIST')
        self._write('*WAI')




"""-----------------------------------------------------------------------------------------------------------------------
Subfunctions for the LockIn have been copied from the zhinst example and slightly adopted. Form the full version checkout: 
https://docs.zhinst.com/labone_api/python/zhinst.examples.hf2.example_scope.html
-----------------------------------------------------------------------------------------------------------------------"""

def get_scope_records(device, daq, scopeModule, num_records=1):
        """
        Obtain scope records from the device using an instance of the Scope Module.
        """

        # Tell the module to be ready to acquire data; reset the module's progress to 0.0.
        scopeModule.execute()

        # Enable the scope: Now the scope is ready to record data upon receiving triggers.
        daq.setInt("/%s/scopes/0/enable" % device, 1)
        daq.sync()

        start = time.time()
        timeout = 1  # [s]
        records = 0
        progress = 0
        # Wait until the Scope Module has received and processed the desired number of records.
        while (records < num_records) or (progress < 1.0):
            time.sleep(0.5)
            records = scopeModule.getInt("scopeModule/records")
            progress = scopeModule.progress()[0]
            #print(("Scope module has acquired {} records (requested {}). "
            #    "Progress of current segment {}%.").format(records, num_records, 100.*progress))
            data = scopeModule.read(True)
            
            
            if (time.time() - start) > timeout:
                # Break out of the loop if for some reason we're no longer receiving scope data from the device.
                print("\nScope Module did not return {num_records} records after {timeout} s - forcing stop.")
                break
        print("")
        daq.setInt("/%s/scopes/0/enable" % device, 0)

        # Read out the scope data from the module.
        #data = scopeModule.read(True)

        # Stop the module; to use it again we need to call execute().
        scopeModule.finish()

        return data

def check_scope_record_flags(scope_records):
        num_records = len(scope_records)
        for index, record in enumerate(scope_records):
            if record[0]["flags"] & 1:
                print("Warning: Scope record {index}/{num_records} flag indicates dataloss.")
            if record[0]["flags"] & 2:
                print("Warning: Scope record {index}/{num_records} indicates missed trigger.")
            if record[0]["flags"] & 4:
                print("Warning: Scope record {index}/{num_records} indicates transfer failure (corrupt data).")
            totalsamples = record[0]["totalsamples"]
            for wave in record[0]["wave"]:
                # Check that the wave in each scope channel contains the expected number of samples.
                assert len(wave) == totalsamples, "Scope record {index}/{num_records} size does not match totalsamples."



class FeedbackLoop( SMIQ ):

    def __init__(self, signal_input, signal_output, start_frequency):
        #SMIQ()
        

        self.signal_input = signal_input
        self.signal_output = signal_output
        self.visa_address = signal_output
        self.frequency = start_frequency  

        self._run() 




    def _run(self): 
        """================================variable decleration ================================"""
        self.outgoingData = 0.0 
        nan = None     


        """-----------------------------------------------------------------------------------------------------------------------
        Settings for the LockIn, 
        
        has been copyed from the zhinst example and slitly adopted. Form the full version checkout:
        https://docs.zhinst.com/labone_api/python/zhinst.examples.hf2.example_scope.html
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
        scope_settings = [[ "/%s/scopes/0/channel" % (device), scope_inputselect],["/%s/scopes/0/bwlimit" % (device), 1],["/%s/scopes/0/time" % (device), 0],["/%s/scopes/0/enable" % device, 1],]
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
        scopeModule.set('scopeModule/mode', 1)
        # 'averager/weight' : Averager behaviour.
        #   weight=1 - don't average.
        #   weight>1 - average the scope record shots using an exponentially weighted moving average.
        scopeModule.set('scopeModule/averager/weight', module_averaging_weight)
        # 'historylength' : The number of scope records to keep in the Scope Module's memory, when more records
        #   arrive in the Module from the device the oldest records are overwritten.
        scopeModule.set('scopeModule/historylength', module_historylength)

        scope_channel_lookup = {0: 'sigin0', 1: 'sigin1', 2: 'sigout0', 3: 'sigout1'}
        scope_channel = scope_channel_lookup[scope_inputselect]
        if scope_channel == 'sigin0':
            externalscaling = daq.getDouble('/{}/sigins/0/range'.format(device))
        elif scope_channel == 'sigin1':
            externalscaling = daq.getDouble('/{}/sigins/1/range'.format(device))
        elif scope_channel == 'sigout0':
            externalscaling = daq.getDouble('/{}/sigouts/0/range'.format(device))
        elif scope_channel == 'sigout1':
            externalscaling = daq.getDouble('/{}/sigouts/1/range'.format(device))
        scopeModule.set('scopeModule/externalscaling', externalscaling)

        # Subscribe to the scope's data in the module.
        wave_nodepath = '/{}/scopes/0/wave'.format(device)
        scopeModule.subscribe(wave_nodepath)



        def _readData(self): 
            """-----------------------------------------------------------------------------------------------------------------------
            The actual reading function is defined inside LockIn Class, here they are just called. 
            
            Notice: 
            The reading function returns a nested dictionary with several measurements inside. As incomingData, just one of
            them is returned as Array. 
            -----------------------------------------------------------------------------------------------------------------------"""
            result = get_scope_records( self.signal_input, daq, scopeModule)   
            self.incomingData = array((((result['/%s/scopes/0/wave' % (device)])[0])[0])['wave'][0])

            return self.incomingData
        
        
        
        def _calculation(self,incomingData): 
            """-----------------------------------------------------------------------------------------------------------------------
            Here the actual calculation will be done. 
            For testing purposes, there is no fancy calculation.   
            -----------------------------------------------------------------------------------------------------------------------"""
            self.outgoingData =self.frequency + average(self.incomingData)

            return self.outgoingData



        def _writeData(self, outgoingData): 
            """-----------------------------------------------------------------------------------------------------------------------
            Calls for the SMIQ API to write the new frequency. 
            -----------------------------------------------------------------------------------------------------------------------"""
            SMIQ.setFrequency(self, outgoingData)
            
            return 

        ############################################################################################################################
        
        
        
        while True:
            """-----------------------------------------------------------------------------------------------------------------------
            The actual infinite loop 
            -----------------------------------------------------------------------------------------------------------------------"""
            try:
                _writeData(self, _calculation(self, _readData(self)))
                self.frequency =  self.outgoingData 
                
                time.sleep(0.001)
            finally:
                print self.frequency
                pass





"""-----------------------------------------------------------------------------------------------------------------------
Every time main.py is called this function will execute the class above. The call for the class should be implemented in the main program. 
Here it just added for testing purposes.
-----------------------------------------------------------------------------------------------------------------------"""

if __name__ == "__main__":
    FeedbackLoop("dev1492", "GPIB0::28", 1e6 )
