'''
Defines an asynchronous listener for listening to events generated by a
serially-connected TinyOS sensor.
'''
import asyncio, io
import serial
import tinyos


class Listener:
    '''
    Implements an asynchronous event listener on a serial device.
    
    The Listener can be in one of three states:
        ACTIVE
        PAUSED
        STOPPED
    '''

    # The various states that the listener can be in
    ACTIVE = 0
    PAUSED = 1
    STOPPED = 2

    def __init__(self, callback, device, baudrate, samplerate):
        self._callback = callback
        self._device = device
        self._baudrate = baudrate
        self._samplerate = samplerate
        self._state = Listener.STOPPED
        self._task = None


    async def _listen(self):
        '''
        Private method that defines the listening task.
        '''
        try:
            # open the serial port on the specified device
            ser = serial.Serial(self._device, baudrate=self._baudrate)
            # wrap the serial device
            sio = io.TextIOWrapper(io.BufferedWRPair(ser, ser))
            while self._state != Listener.STOPPED:
                # read from the datastream
                line = sio.readline()
                # check if there was data
                if line:
                    # call the callback function
                    self._callback(line)
                # wait for the specified amount of time
                await asyncio.sleep(1/self._sampling_rate)
            # close the serial device
            ser.close()
        except SerialException:
            self._listening = False
            print('Unable to connect to serial device...')


    async def start(self):
        '''
        Starts listening for events.
        '''
        if self._state == Listener.STOPPED:
            loop = asyncio.get_event_loop()
            self._task = loop.create_task(listen())

            try:
                self._state = Listener.ACTIVE
                loop.run_until_complete(self._task)
            except asyncio.CancelledError:
                pass


    async def stop(self):
        '''
        Stops listening for events.
        '''
        if (self._state == Listener.ACTIVE or 
                self._state == Listener.PAUSED):
            await self._task.cancel()
            self._state = Listener.STOPPED
        
        
    def pause(self):
        '''
        Pauses listening for events.
        '''
        if self._state == Listener.ACTIVE:
            self._state = Listener.PAUSED
            
    
    def resume(self):
        '''
        Resumes listening for events.
        '''
        if self._state == Listener.PAUSED:
            self._state = Listener.ACTIVE
    
    
    def 
