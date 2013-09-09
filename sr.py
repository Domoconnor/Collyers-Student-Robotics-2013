class Primitive(object):
    def __init__( self, renderer ):
        self.renderer = renderer

    def draw( self, pixel ):
        pass

class Box(object):
    def __init__( self, renderer, x, y, width, height ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        Primitive.__init__( self, renderer )

class Arena(object):
    def __init__( self ):
        pass

    def dump( self ):
        print_acc = ""
        for y in xrange( 8 ):
            for i in xrange( 3 ):
                line = ""
                for x in xrange( 8 ):
                    for j in xrange( 4 ):
                        line += "#"
                    line += "|"
                print_acc += line + "\n"
            line = ""
            for i in xrange( 4 * 8 ):
                line += "-"
            print_acc += line + "\n"
        print print_acc

class Robot(object):
    def __init__( self ):
        self.arena = Arena()
        self.arena.dump()

    def update( self ):
        self.arena.dump()

R = Robot()
