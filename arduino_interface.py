
from common import *
import serial
import task

class Arduino(object):
    def __init__( self ):
        self.grabbed = False
        self.serial = None
        try:
            self.serial = serial.Serial( "/dev/ttyACM0", 9600, timeout = 1 )
        except serial.serialutil.SerialException:
            log( "Arduino", "Unable to open serial port to arduino" )

    # High Level Interface
    def set_heli_speed( self, speed ):
        assert( speed >= -100 )
        assert( speed <= 100 )
        self._arduino_set_heli_speed( int( speed ) + 100 )
        log( "Arduino", "Set heli speed to {0}".format( speed ) )

    def set_grabber_speed( self, speed ):
        assert( speed >= -100 )
        assert( speed <= 100 )
        self._arduino_set_grabber_speed( int( speed ) + 100 )
        log( "Arduino", "Set grabber speed to {0}".format( speed ) )

    # Send op code and operand for each of these functions
    # speed MUST be an int type
    def _arduino_set_heli_speed( self, speed ):
        if self.serial:
            self.serial.write( chr( 33 ) )
            self.serial.write( chr( speed ) )
            log( "Arduino", "Writing {0} {1} to serial".format( chr( 33 ), chr( speed ) ) )

    def _arduino_set_grabber_speed( self, speed ):
        if self.serial:
            self.serial.write( chr( 34 ) )
            self.serial.write( chr( speed ) )
            log( "Arduino", "Writing {0} {1} to serial".format( chr( 34 ), chr( speed ) ) )

arduino = None

class RunHeli(task.Base):
    def __init__( self, time ):
        self.time = time

    def main( self ):
        arduino.set_heli_speed( 100 )
        time.sleep( self.time )
        arduino.set_heli_speed( 0 )

class Grab(task.Base):
    def main( self ):
        if arduino.grabbed == False:
            arduino.set_grabber_speed( 100 )
            time.sleep( 5 )
            arduino.set_grabber_speed( 0 )
            arduino.grabbed = True

class Drop(task.Base):
    def main( self ):
        if arduino.grabbed == True:
            arduino.set_grabber_speed( -100 )
            time.sleep( 5 )
            arduino.set_grabber_speed( 0 )
            arduino.grabbed = False
