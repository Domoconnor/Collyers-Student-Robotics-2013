from common import *
import heapq
import copy
import vision

class Cell(object):
    def __init__( self, position, reachable ):
        self.position = position
        self.reachable = reachable
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

class Map(object):
    # Positions in the array are defined as where two lines intersect in an 8m x 8m grid
    def __init__( self ):
        self.robots = {}
        self.tokens = {}
        
        # Figure out starting point based on zone number
        z = r_instance.R.zone
        self.starting_position = Position( 0, 0 )
        if z == 0:
            self.starting_position = Position( 0.25, 0.25 )
        elif z == 1:
            self.starting_position = Position( 7.75, 0.25 )
        elif z == 2:
            self.starting_position = Position( 7.75, 7.75 )
        else:
            self.starting_position = Position( 0.25, 7.75 )

        # Initialise the grid
        self.grid = [Cell( Position( x, y ), True ) for y in xrange( 7 ) for x in xrange( 7 )]
        for x in xrange( 7 ):
            for y in xrange( 7 ):
                if x % 2 == 1 and y % 2 == 1:
                    self.get_cell( Position( x, y ) ).reachable = False
        self.dump()

        # Set up the A* algorithm
        self.start = None
        self.end = None
        
    def is_our_token( self, marker ):
        numbers = [range(41, 47), range(47, 53), range(53, 59), range(59, 65)]
        code = marker.info.code
        if code in numbers[r_instance.R.zone]:
            return True
        else:
            return False

    def set_grid_reachable( self, position, reachable ):
        grid_pos = self.align_to_grid( position )
        self.get_cell( grid_pos ).reachable = reachable

    def get_cell( self, position ):
        return self.grid[position.x + position.y * 7]

    def align_to_grid( self, position ):
        int_x = int( round( position.x ) ) - 1
        int_y = int( round( position.y ) ) - 1
        if int_x < 0:
            int_x = 0
        if int_x > 6:
            int_x = 6
        if int_y < 0:
            int_y = 0
        if int_y > 6:
            int_y = 6
        return Position( int_x, int_y )

    def set_robot_position( self, robot_id, position ):
        assert( robot_id != r_instance.R.zone )
        self.robots[robot_id] = position

    def get_robot_position( self, robot_id ):
        assert( robot_id != r_instance.R.zone )
        return self.robots[robot_id]

    def update_token( self, m ):
        assert( m.info.marker_type == MARKER_TOKEN )
        self.tokens[m.info.code] = vision.vision.current_position

    def get_token_position( self, marker_code ):
        return self.tokens[marker_code]

    # Dump the current map to the log
    def dump( self ):
        log( "Map", "Dumping the current map. 0 = free, 1 = pedestal" )
        for y in xrange( 7 ):
            line_str = ""
            for x in xrange( 7 ):
                if self.get_cell( Position( x, y ) ).reachable == True:
                    line_str += "0"
                else:
                    line_str += "1"
            log( "Map", line_str )

    # Pathfinding through the 7x7 grid
    # Returns the set of waypoints and a bool to indicate success or failure
    def get_path( self, position, target ):
        path = self.calculate_new_path( position, target )
        if len( path ) == 0:
            return [], False
        return reversed( path ), True

    def calculate_new_path( self, position, target ):
        self.start = self.get_cell( self.align_to_grid( position ) )
        self.end = self.get_cell( self.align_to_grid( target ) )

        open_list = []
        heapq.heapify( open_list )
        closed_list = set()

        # add starting cell to open heap queue
        heapq.heappush( open_list, ( self.start.f, self.start ) )
        while len( open_list ):
            # pop cell from heap queue 
            f, cell = heapq.heappop( open_list )

            # add cell to closed list so we don't process it twice
            closed_list.add( cell )

            # if ending cell, display found path
            if cell is self.end:
                return self.get_final_path()

            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells( cell )
            for c in adj_cells:
                if c.reachable and c not in closed_list:
                    if ( c.f, c ) in open_list:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found for this adj
                        # cell.
                        if c.g > cell.g + 10:
                            self.update_cell( c, cell )
                    else:
                        self.update_cell( c, cell )
                        # add adj cell to open list
                        heapq.heappush( open_list, ( c.f, c ) )

        # Couldnt find a path
        return []

    def get_adjacent_cells(self, cell):
        cells = []
        if cell.position.x < 6:
            cells.append( self.get_cell( Position( cell.position.x + 1, cell.position.y ) ) )
        if cell.position.y > 0:
            cells.append( self.get_cell( Position( cell.position.x, cell.position.y - 1 ) ) )
        if cell.position.x > 0:
            cells.append( self.get_cell( Position( cell.position.x - 1, cell.position.y ) ) )
        if cell.position.y < 6:
            cells.append( self.get_cell( Position( cell.position.x, cell.position.y + 1 ) ) )
        return cells

    def get_heuristic( self, cell ):
        return 10 * ( abs( cell.position.x - self.end.position.x ) + abs( cell.position.y - self.end.position.y ) )

    def update_cell( self, adj, cell ):
        adj.g = cell.g + 10
        adj.h = self.get_heuristic( adj )
        adj.parent = cell
        adj.f = adj.h + adj.g

    def get_final_path( self ):
        cell = self.end
        path = [ copy.deepcopy( cell.position ) ]
        while cell.parent is not self.start:
            cell = cell.parent
            path.append( copy.deepcopy( cell.position ) )
        path.append( copy.deepcopy( self.start.position ) )
        return path

game_map = None