from common import *
import task
import control
import vision
import game_map
import arduino_interface

# Align the robot to a marker and pick it up
class GrabToken(task.Base):
    def __init__( self, marker ):
        self.marker = marker

    def main( self ):
        # Get alpha + beta and calculate trig stuff
        x = self.marker.dist
        alpha = math.radians( self.marker.orientation.rot_y )
        beta = math.radians( self.marker.rot_y )
        log( "GrabMarker", "x = {0} alpha = {1} beta = {2}".format( x, math.degrees( alpha ), math.degrees( beta ) ) )

        # Calcuate theta, d1, look_at, d2
        theta = math.pi * 0.5 - abs( beta ) - abs( alpha )
        d1 = x * math.sin( abs( beta ) )
        d2 = x * math.cos( abs( beta ) )
        look_at = math.pi * 0.5
        if beta > 0:
            theta *= -1
        else:
            look_at *= -1
        log( "GrabMarker", "theta = {0} d1 = {1} look_at = {2} d2 = {3}".format( math.degrees( theta ), d1, math.degrees( look_at ), d2 ) )

        # Move by d1, rotate by theta, move by d2
        task.pool.execute( control.RotateTask( theta, 0.75 ) )
        if d1 > 0.01:
         task.pool.execute( control.MoveTask( d1, 0.75 ) )
        task.pool.execute( control.RotateTask( look_at, 0.75 ) )
        if d2 > 0.01:
            task.pool.execute( control.MoveTask( d2, 0.75 ) )

# Work out current position
class FigureOutPosition(task.Base):
    def main( self ):
        success = False
        while not success:
            for i in xrange( 9 ):
                markers, success = vision.vision.capture()
                if success:
                    break
                else:
                    task.pool.execute( control.RotateTask( math.pi * 0.2 ) )
            task.pool.execute( control.MoveTask( -1 ) )
            for i in xrange( 9 ):
                markers, success = vision.vision.capture()
                if success:
                    break
                else:
                    task.pool.execute( control.RotateTask( math.pi * 0.2 ) )
            task.pool.execute( control.MoveTask( 2, 1.5 ) )

# Calculate a new path and follow it
class MoveToNextPoint(task.Base):
    def __init__( self, target ):
        self.target = target

    def get_middle_square( self, position ):
        grid_pos = game_map.game_map.align_to_grid( position )
        return Position( float( grid_pos.x ) + 0.5, float( grid_pos.y ) + 0.5 )

    def get_initial_rotate( self, node ):
        delta_pos = node

        # Each node will either be directly north, east, south or west from the previous one
        rotate = 0
        if delta_pos.x == 0:
            if delta_pos.y > 0:
                rotate = math.pi
            else:
                rotate = 0
        if delta_pos.y == 0:
            if delta_pos.x > 0:
                rotate = math.pi * 0.5
            else:
                rotate = math.pi * 1.5
        rotate -= vision.vision.current_heading

        # If the rotation > pi radians, rotate the other way instead
        if rotate < -math.pi:
            rotate += math.pi * 2
        if rotate > math.pi:
            rotate -= math.pi * 2
            
        return rotate

    def get_rotate_then_move_amount( self, node_a, node_b, current_heading ):
        delta_pos = node_b - node_a

        # Each node will either be directly north, east, south or west from the previous one
        rotate = 0
        move = 0
        if delta_pos.x == 0:
            if delta_pos.y > 0:
                rotate = math.pi - current_heading
            else:
                rotate = - current_heading
            move = abs( delta_pos.y )
        if delta_pos.y == 0:
            if delta_pos.x > 0:
                rotate = math.pi * 0.5 - current_heading
            else:
                rotate = math.pi * 1.5 - current_heading
            move = abs( delta_pos.x )

        # If the rotation > pi radians, rotate the other way instead
        if rotate < -math.pi:
            rotate += math.pi * 2
        if rotate > math.pi:
            rotate -= math.pi * 2

        return rotate, move

    def main( self ):
        # We need to move to the middle of the metre square that we're in
        current_middle_square = self.get_middle_square( vision.vision.current_position )
        target_middle_square = self.get_middle_square( self.target )

        # Calculate a new path to the target
        game_map.game_map.dump()
        benchmark_begin( "game_map.get_path" )
        path, success = game_map.game_map.get_path( current_middle_square, target_middle_square )
        benchmark_end()
        if not success:
            log( "MoveToNextPoint", "Unable to find a path to the target, aborting task!" )
            return

        # First move to the middle of the current square
        movement_tasks = []
        cp = vision.vision.current_position
        ch = vision.vision.current_heading
        log( "MoveToNextPoint", "cp: ({0}, {1}) - ch: {2}".format( cp.x, cp.y, ch ) )
        pos_in_square = Position( math.fmod( cp.x, 1.0 ), math.fmod( cp.y, 1.0 ) )
        heading_to = pos_in_square.heading_to( Position( 0.5, 0.5 ) ) - ch
        if heading_to < -math.pi:
            heading_to += math.pi * 2
        if heading_to > math.pi:
            heading_to -= math.pi * 2
        movement_tasks.append( control.RotateTask( heading_to ) )

        # Translate these waypoint into movement tasks
        first_node = True
        prev_node = None
        prev_heading = 0
        accumulate_move = 0
        for node_id, node in enumerate( path ):
            log( "MoveToNextPoint", "Node {0} - position = ({1},{2})".format( node_id, node.x, node.y ) )
            heading = 0
            if prev_node != None:
                if first_node == True:
                    # Initial alignment to the first node
                    rotate = self.get_initial_rotate( node )
                    heading = rotate + vision.vision.current_heading
                    movement_tasks.append( control.RotateTask( rotate ) )
                    first_node = False
                    log( "MoveToNextPoint", "Initial alignment - correction of {0} degrees".format( math.degrees( rotate ) ) )
                else:
                    # Node to node
                    rotate, move = self.get_rotate_then_move_amount( prev_node, node, prev_heading )
                    if abs( rotate ) > 1e-6:
                        movement_tasks.append( control.MoveTask( accumulate_move ) )
                        movement_tasks.append( control.RotateTask( rotate ) )
                        accumulate_move = 0
                    accumulate_move += move
                    heading = prev_heading + rotate
                    log( "MoveToNextPoint", "{0} -> {1}: Rotate by {2} degrees and move by {3} metres".format( node_id - 1, node_id, math.degrees( rotate ), move ) )
            prev_heading = heading
            prev_node = node

        # Execute these movement tasks
        task.pool.add_set_next( movement_tasks )

# Marker Test
class SearchForToken(task.Base):
    def main( self ):
        # Look for a token
        marker_id = -1
        marker = None
        while marker_id == -1:
            markers, success = vision.vision.capture()
            if len( markers ) > 0:
                for m in markers:
                    if m.info.marker_type == MARKER_TOKEN:
                        marker_id = m.info.code
                        marker = m
                        break
            if marker_id == -1:
                log( "MarkerTest", "Didn't find a marker, rotating 45 degrees" )
                task.pool.execute( control.RotateTask( math.pi * 0.25 ) )
                task.pool.execute( task.Sleep( 0.25 ) )

        # Once we see a token, grab it for the lols
        task.pool.add_next( GrabToken( marker ) )

# Display battery settings
def dump_battery():
    percentage = ( r_instance.R.power.battery.voltage - 10 ) * 100 / 2.6
    log( "Robot", "Battery Voltage = {0} - Battery Current = {1}".format( r_instance.R.power.battery.voltage, r_instance.R.power.battery.current ) )
    log( "Robot", "Approx. Battery Percentage = {0}%".format( percentage ) )

class TokenCorrection(task.Base):
    def __init__( self, marker_to_ignore ):
        self.ignore = marker_to_ignore
        
    def main( self ):
        found_our_token = False
        correction = 0
        calc_dir = 1
        no_iterations = 0
        first_move = True
        while not found_our_token and no_iterations < 6:
            markers = vision.vision.capture()[0]
            for m in markers:
                if m.info.marker_type == MARKER_TOKEN and m.info.code != self.ignore:
                    # Probably our token, see what the correction is
                    correction = math.radians( m.rot_y )
                    found_our_token = True
                    log( "TokenCorrection", "Saw our token, correction needed = {0}".format( correction ) )
                    task.pool.execute( control.RotateTask( correction ) )
                    break
            if not found_our_token:
                # Didn't see our token, moved too far in a direction so turn one way and look again
                if no_iterations % 2 == 1:
                    calc_dir = -calc_dir
                task.pool.execute( control.RotateTask( math.pi * 0.125 * calc_dir ) )
                time.sleep( 0.25 )
                log( "TokenCorrection", "Didn't see our token :(" )
            no_iterations += 1

# Main
def main():
    r_instance.R = Robot()
    set_debug_mode( True )
    dump_battery()

    # Initialise modules
    task.pool = task.TaskPool()
    control.control = control.Control()
    vision.vision = vision.Vision()
    arduino_interface.arduino = arduino_interface.Arduino()
    game_map.game_map = game_map.Map()

    # Move initial token
    task.pool.execute( control.MoveTask( 1.2 ) )
    task.pool.execute( control.MoveTask( -0.6 ) )
    tokens = vision.vision.capture()[0]
    our_marker_id = 0
    if len( tokens ) > 0:
        our_marker_id = tokens[0].info.code
    log( "Robot", "our_marker_id = {0}".format( our_marker_id ) )
    task.pool.execute( control.MoveTask( -0.7 ) )
    
    # Look at remaining tokens and move into them
    task.pool.execute( control.RotateTask( -math.pi * 0.35 ) )

    # Attempt to correct itself
    task.pool.execute( TokenCorrection( our_marker_id ) )
    task.pool.execute( control.MoveTask( 0.775 ) )
    for i in xrange( 2 ):
        task.pool.execute( control.RotateTask( math.pi * 0.4, 3.0 ) )
        task.pool.execute( control.MoveTask_Stepper( 2.0, 3.0, 8 ) )

    
    """
    # Move away, turn 180 degrees then calibrate
    task.pool.add( control.MoveTask( -1.5 ) )
    task.pool.add( control.RotateTask( -math.pi * 0.5 ) )
    task.pool.add( control.MoveTask( 2, 0.75 ) )
    
    # Now we know where we are, move to where our tokens reside and grab one
    target_point = game_map.game_map.starting_position
    target_point.x = 8 - target_point.x
    task.pool.add( FigureOutPosition() )
    task.pool.add( MoveToNextPoint( target_point ) )
    task.pool.add( SearchForToken() )
    task.pool.add( control.RotateTask( -math.pi * 0.5 ) )
    task.pool.add( control.MoveTask( 2 ) )
    task.pool.add( control.MoveTask( -1 ) )
    
    # Move to the middle square
    task.pool.add( FigureOutPosition() )
    task.pool.add( MoveToNextPoint( Position( 5, 5 ) ) )
    """
    
    # Enter the main loop
    task.pool.execute( task.ExitLoop() )
    task.pool.run()

    # Final words..
    log( "Robot", "Task queue finished executing, exiting..." )
    dump_battery()

# Run main
main()