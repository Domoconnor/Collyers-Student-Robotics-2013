from common import *
import task

# Handles the control of the robot
class Control(object):
    def __init__( self ):
        # 2.5m in 3s forwards/backwards
        # 3.6 turns right in 10s
        # 3.2 turns left in 10s
        self.move_speed = ( 0.523, 0.523 ) # Forwards, Backwards
        self.rotate_speed = ( 1.5, 1.5 ) # Right (positive), Left (negative)

        self.move_speed_with_token = ( 0.3, 0.3 )
        self.rotate_speed_with_token = ( 1.1, 1.1 )

        self.holding_token = False

    def set_move_power( self, power ):
        r_instance.R.motors[0].target = -power
        r_instance.R.motors[1].target = -power
        log( "Control", "Set Motor 0 to {0} and Motor 1 to {0}".format( -power ) )

    def set_rotate_power( self, power ):
        r_instance.R.motors[0].target = power
        r_instance.R.motors[1].target = -power
        log( "Control", "Set Motor 0 to {0} and Motor 1 to {1}".format( -power, power ) )

    def stop_motors( self ):
        r_instance.R.motors[0].target = 0
        r_instance.R.motors[1].target = 0
        log( "Control", "Stopped motors" )

control = None

# Tasks
class MoveTask(task.Base):
    def __init__( self, distance, power = 1.0 ):
        self.power = power

        # Calculate direction
        self.direction = 1
        if abs( distance ) > 1e-6:
            self.direction = int( distance / abs( distance ) )

        # Pick the correct speed
        move_speed = 0
        if self.direction == -1:
            if control.holding_token:
                move_speed = control.move_speed_with_token[1]
            else:
                move_speed = control.move_speed[1]
        else:
            if control.holding_token:
                move_speed = control.move_speed_with_token[0]
            else:
                move_speed = control.move_speed[0]

        # Calculate the duration to move for
        self.time = abs( distance ) / ( move_speed * power )

    def main( self ):
        control.set_move_power( 30 * self.direction * self.power )
        time.sleep( self.time )
        control.stop_motors()
        
        
class MoveTask_Stepper(task.Base):
    def __init__( self, distance, max_power, steps ):
        self.max_power = max_power
        self.steps = steps

        # Calculate direction
        self.direction = 1
        if abs( distance ) > 1e-6:
            self.direction = int( distance / abs( distance ) )

        # Pick the correct speed
        move_speed = 0
        if self.direction == -1:
            if control.holding_token:
                move_speed = control.move_speed_with_token[1]
            else:
                move_speed = control.move_speed[1]
        else:
            if control.holding_token:
                move_speed = control.move_speed_with_token[0]
            else:
                move_speed = control.move_speed[0]

        # Calculate the duration to move for
        self.time = abs( distance ) / ( move_speed )

    def main( self ):
        t = self.time / self.steps
        delta_step = ( self.max_power - 1 ) / ( self.steps / 2 )
        for i in xrange( self.steps / 2 ):
            control.set_move_power( 30 * self.direction * ( 1.0 + delta_step * i ) )
            time.sleep( t )
        for i in reversed( xrange( self.steps / 2 ) ):
            control.set_move_power( 30 * self.direction * ( 1.0 + delta_step * i ) )
            time.sleep( t )
        control.stop_motors()

class RotateTask(task.Base):
    def __init__( self, angle, power = 1.0 ):
        self.power = power

        # Calculate direction
        self.direction = 1
        if abs( angle ) > 1e-6:
            self.direction = int( angle / abs( angle ) )

        # Pick the correct speed
        rotate_speed = 0
        if self.direction == -1:
            if control.holding_token:
                rotate_speed = control.rotate_speed_with_token[1]
            else:
                rotate_speed = control.rotate_speed[1]
        else:
            if control.holding_token:
                rotate_speed = control.rotate_speed_with_token[0]
            else:
                rotate_speed = control.rotate_speed[0]

        # Calculate the duration to move for
        self.time = abs( angle ) / ( rotate_speed * power )

    def main( self ):
        control.set_rotate_power( 30 * self.direction * self.power )
        time.sleep( self.time )
        control.stop_motors()

class MoveTask_Seconds(task.Base):
    def __init__( self, time, direction, power = 1 ):
        self.power = power
        self.direction = int( direction )
        self.time = time

    def main( self ):
        control.set_move_power( 30 * self.direction * self.power )
        time.sleep( self.time )
        control.stop_motors()

class RotateTask_Seconds(task.Base):
    def __init__( self, time, direction, power = 1 ):
        self.power = power
        self.direction = int( direction )
        self.time = time

    def main( self ):
        control.set_rotate_power( 30 * self.direction * self.power )
        time.sleep( self.time )
        control.stop_motors()