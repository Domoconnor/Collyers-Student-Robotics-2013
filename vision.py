from common import *
import game_map

class Vision(object):
    def __init__( self ):
        self.current_position = Position( 0, 0 )
        self.current_heading = 0
        self.last_position = Position( 0, 0 )
        self.last_heading = 0
        self.cam_width = 1280
        self.cam_height = 960

    def set_res( self, width, height ):
        self.cam_width = width
        self.cam_height = height

    def capture( self ):
        markers = r_instance.R.see( res = ( self.cam_width, self.cam_height ) )
        log( "Vision", "{0} markers visible".format( len( markers ) ) )

        for m_id, m in enumerate( markers ):
            log( "Vision", "{0}: x = {1} y = {2} z = {3}".format( m_id, m.centre.world.x, m.centre.world.y, m.centre.world.z ) )
            log( "Vision", "{0}: rot = {1} orient = {2} code = {3} type = {4}".format( m_id, m.rot_y, m.orientation.rot_y, m.info.code, m.info.marker_type ) )

        # Calculate new position and heading
        success = False
        for m in markers:
            if m.info.marker_type == MARKER_ARENA:
                self.last_position = self.current_position
                self.last_heading = self.current_heading
                self.current_position, self.current_heading = self.get_location_from_wall( m )
                success = True
                break

        return markers, success

    def get_location_from_wall( self, marker ):
        """ Takes marker object as a parameter. Should be MAr_instance.RKEr_instance.R_Ar_instance.RENA
            r_instance.Returns ( Position, o ) origin being top-left corner of arena
            Position - coordinates in meters; o - orientation in radians
        """
        n = marker.info.code
        alpha = math.radians( marker.rot_y )
        beta = math.radians( marker.orientation.rot_y )
        dist = marker.dist
        w = n // 7
        d = n % 7 + 1
        if w == 0:
            y = d - math.sin( beta ) * dist
            x = math.cos( beta ) * dist
            o = math.pi * 1.5 - alpha - beta
        elif w == 1:
            y = 8 - math.cos( beta ) * dist
            x = d - math.sin( beta ) * dist
            o = math.pi - alpha - beta
        elif w == 2:
            y = 8 - d + math.sin( beta ) * dist
            x = 8 - math.cos( beta ) * dist
            o = math.pi * 0.5 - alpha - beta
        else:
            y = math.cos( beta ) * dist
            x = 8 - d + math.sin( beta ) * dist
            o = - alpha - beta
        if o < 0:
            o += math.pi * 2
        log( "Vision", "Robot: x = {0}, y = {1}, o = {2}".format( x, y, math.degrees( o ) ) )
        return Position( x, y ), o

vision = None