from sr import *
from collections import deque
import time
import datetime as dt
import math
import r_instance

debug_enabled = True
benchmark_start = 0
log_file = None

# Class which stores a two dimensional position from the top left of the arena (the origin)
class Position(object):
    """
    Usage:
        pos1 = Position( 2, 3 )
        pos2 = pos1 * 2
        print pos2.x, pos2.y
    Output:
        4 6
    """

    def __init__( self, x = 0, y = 0 ):
        self.x = x
        self.y = y

    def __add__( self, other ):
        return Position( self.x + other.x, self.y + other.y )

    def __sub__( self, other ):
        return Position( self.x - other.x, self.y - other.y )

    # Scale this position by a single value
    def __mul__( self, other ):
        return Position( self.x * other, self.y * other )

    def distance( self, other ):
        delta_pos = self - other
        return math.sqrt( delta_pos.x ** 2 + delta_pos.y ** 2 )

    def heading_to( self, other ):
        delta_pos = other - self
        return math.fmod( math.atan2( delta_pos.y, delta_pos.x ) + math.pi * 0.5, math.pi * 2 )

# Benchmarking
def benchmark_begin( name ):
    global debug_enabled
    global benchmark_start
    if debug_enabled == True:
        benchmark_start = dt.datetime.now().microsecond
        log( "Benchmark", "Began benchmarking - " + name )

def benchmark_end():
    global debug_enabled
    global benchmark_start
    if debug_enabled == True:
        time_elapsed = ( dt.datetime.now().microsecond - benchmark_start ) * 1e-6
        log( "Benchmark", "Finished benchmarking - Time elapsed: {0}".format( time_elapsed ) )

# Debug mode
def set_debug_mode( debug ):
    global debug_enabled
    debug_enabled = debug

# Logging
def log( module_name, message ):
    global debug_enabled
    if debug_enabled == True:
        print "[{0}] {1}".format( module_name, message )
