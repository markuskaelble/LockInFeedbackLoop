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


class FeedbackLoop( SMIQ ):

    def __init__(self, signal_input, signal_output, start_frequency):

        

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
       
        """================================API configurations================================"""

        (daq, device, props) = zhinst.utils.create_api_session(self.signal_input, 1, required_devtype="HF2", required_err_msg='Nope')


        def _readData(self): 
            """-----------------------------------------------------------------------------------------------------------------------
            The actual reading function is defined inside LockIn Class, here they are just called. 
            
            Notice: 
            The reading function returns a nested dictionary with several measurements inside. As incomingData, just one of
            them is returned as Array. 
            -----------------------------------------------------------------------------------------------------------------------"""
            daq.setInt('/dev1492/demods/0/enable', 1)
            daq.setDouble('/dev1492/demods/0/rate', 1e3)
            daq.subscribe('/dev1492/demods/0/sample')

            """===============================================================================
            Just change stuff below 
            ==============================================================================="""
            time.sleep(1) # Subscribed data is being accumulated by the Data Server.
            data_dict = daq.poll(0.1, 1, 0, True) # poll( recording_time_s: float, timeout_ms: int)
            """===============================================================================

            ==============================================================================="""
           
            self.incomingData = data_dict['/dev1492/demods/0/sample']['x'] # gets x values
 
            return self.incomingData
        
        
        
        def _calculation(self,incomingData): 
            """-----------------------------------------------------------------------------------------------------------------------
            Here the actual calculation will be done. 
            For testing purposes, there is no fancy calculation.   
            -----------------------------------------------------------------------------------------------------------------------"""
            
            self.outgoingData =self.frequency - average(self.incomingData)*5.4113e+7

            """
            averageData = average(self.incomingData)

            if averageData >= 0:
                self.outgoingData =self.frequency - 100
            else:
                self.outgoingData =self.frequency + 100
            """
            

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
                print average(self.incomingData)
                pass





"""-----------------------------------------------------------------------------------------------------------------------
Every time main.py is called this function will execute the class above. The call for the class should be implemented in the main program. 
Here it just added for testing purposes.
-----------------------------------------------------------------------------------------------------------------------"""

if __name__ == "__main__":
    FeedbackLoop("dev1492", "GPIB0::28", 2899.87950e6 )
