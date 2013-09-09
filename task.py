
from common import *

# Base class for a task
class Base(object):
    def main( self ):
        pass

# Executes tasks
class TaskPool(object):
    def __init__( self ):
        self.task_queue = deque()
        self.exit_flag = False
        self.current_task = None
        self.insert_next_rotation = 0

    # Execute a task immediately (interrupt current task)
    def execute( self, task ):
        task.main()

    # Add a task after the currently executing task
    def add_next( self, task ):
        self.task_queue.appendleft( task )

    # Add a set of tasks after the currently executing task
    def add_set_next( self, task_set ):
        # As we're appending to the front add the tasks in reverse order
        for task in reversed( task_set ):
            self.add_next( task )

    # Add a task to the end of the queue
    def add( self, task ):
        self.task_queue.append( task )

    # Add a set of tasks to the end of the queue
    def add_set( self, task_set ):
        for task in task_set:
            self.add( task )
    
    # Run through all the tasks in the queue
    def run( self ):
        while self.exit_flag == False:
            if len( self.task_queue ) > 0:
                self.current_task = self.task_queue.popleft()
                self.execute( self.current_task )

pool = None

# Sleep
class Sleep(Base):
    def __init__( self, time ):
        self.time = time
        
    def main( self ):
        time.sleep( self.time )

# Exit the task loop
class ExitLoop(Base):
    def main( self ):
        pool.exit_flag = True
        