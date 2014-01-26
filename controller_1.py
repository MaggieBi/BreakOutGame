# controller.py
# Yunjie Bi (yb89) & Chi Wei Zhang (cz222)
# Dec 3rd, 2012
"""Controller module for Breakout

This module contains a class and global constants for the game Breakout.
Unlike the other files in this assignment, you are 100% free to change
anything in this file. You can change any of the constants in this file
(so long as they are still named constants), and add or remove classes."""
import colormodel
import random
from graphics import *

# CONSTANTS

# Width of the game display (all coordinates are in pixels)
GAME_WIDTH  = 480
# Height of the game display
GAME_HEIGHT = 620

# Width of the paddle
PADDLE_WIDTH = 58
# Height of the paddle
PADDLE_HEIGHT = 11
# Distance of the (bottom of the) paddle up from the bottom
PADDLE_OFFSET = 30

# Horizontal separation between bricks
BRICK_SEP_H = 5
# Vertical separation between bricks
BRICK_SEP_V = 4
# Height of a brick
BRICK_HEIGHT = 8
# Offset of the top brick row from the top
BRICK_Y_OFFSET = 70

# Number of bricks per row
BRICKS_IN_ROW = 10
# Number of rows of bricks, in range 1..10.
BRICK_ROWS = 10
# Width of a brick
BRICK_WIDTH = GAME_WIDTH / BRICKS_IN_ROW - BRICK_SEP_H

# Diameter of the ball in pixels
BALL_DIAMETER = 18

# Number of attempts in a game
NUMBER_TURNS = 3

# Basic game states
# Game has not started yet
STATE_INACTIVE = 0
# Game is active, but waiting for next ball
STATE_PAUSED   = 1
# Ball is in play and being animated
STATE_ACTIVE   = 2
# Game is over, deactivate all actions
STATE_COMPLETE = 3

# ADD MORE CONSTANTS (PROPERLY COMMENTED) AS NECESSARY
#press_label = GLabel(center_x=GAME_WIDTH/2,center_y=GAME_HEIGHT/2,valign = 'middle', halign = 'center',text='Press to Play',font_size=35)#Something about making this global?

# CLASSES

class Caller(object):
    _callback = None
    
    def __init__(self,callback):
        """Creates a Caller with foo() set to use callback."""
        self._callback = callback
    
    def remove (self, n):
        assert type(n) == GLabel
        
        if self._callback == None:
            return
        else:
            self._callback(n)

class Breakout(GameController):
    """Instance is the primary controller for Breakout.

    This class extends GameController and implements the various methods
    necessary for running the game.

        Method initialize starts up the game.

        Method update animates the ball and provides the physics.

        The on_touch methods handle mouse (or finger) input.

    The class also has fields that provide state to this controller.
    The fields can all be hidden; you do not need properties. However,
    you should clearly state the field invariants, as the various
    methods will rely on them to determine game state."""
    # FIELDS.

    # Current play state of the game; needed by the on_touch methods
    # Invariant: One of STATE_INACTIVE, STATE_PAUSED, STATE_ACTIVE
    _state  = STATE_INACTIVE

    # List of currently active "bricks" in the game.
    #Invariant: A list of  objects that are instances of GRectangle (or a
    #subclass) If list is  empty, then state is STATE_INACTIVE (game over)
    _bricks = []

    # The player paddle
    # Invariant: An object that is an instance of GRectangle (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over)
    _paddle = None

    # The ball to bounce about the game board
    # Invariant: An object that is an instance of GEllipse (or a subclass)
    # Also can be None; if None, then state is STATE_INACTIVE (game over) or
    # STATE_PAUSED (waiting for next ball)
    _ball = None

    # ADD MORE FIELDS (AND THEIR INVARIANTS) AS NECESSARY
    
    _prev_mouse = 0
    _dist = 0
    _state_active = False
    
    # The player's game life left
    # Invariant: A positive int in 0 to 3
    # It it is zero, then state is STATE_COMPLETE
    _lives = 3
    
    
    
    # METHODS

    def initialize(self):
        """Initialize the game state.

        Initialize any state fields as necessary to statisfy invariants.
        When done, set the state to STATE_INACTIVE, and display a message
        saying that the user should press to play a game."""
        
        self._state = STATE_INACTIVE
        self._state_active = False
        self.press_label = GLabel(center_x=GAME_WIDTH/2,center_y=GAME_HEIGHT/2,valign = 'middle', halign = 'center',text='Press to Play',font_size=35)
        self.view.add(self.press_label)
        

    def update(self, dt):
        """Animate a single frame in the game.

        This is the method that does most of the work.  It moves the ball, and
        looks for any collisions.  If there is a collision, it changes the
        velocity of the ball and removes any bricks if necessary.

        This method may need to change the state of the game.  If the ball
        goes off the screen, change the state to either STATE_PAUSED (if the
        player still has some tries left) or STATE_COMPLETE (the player has
        lost the game).  If the last brick is removed, it needs to change
        to STATE_COMPLETE (game over; the player has won).

        Precondition: dt is the time since last update (a float).  This
        parameter can be safely ignored."""
        
        if self._state == STATE_INACTIVE or self._state == STATE_PAUSED or self._state == STATE_COMPLETE:
            pass
        else:
            if self._ball != None:
                x = self._ball.pos[0]
                y = self._ball.pos[1]
                self._ball.pos = (x + self._ball._vx, y + self._ball.vy)
            
                if self._ball.top > GAME_HEIGHT:
                    y = self._ball.vy
                    self._ball.vy = (-1)*y
                elif self._ball.right > GAME_WIDTH:
                    x = self._ball._vx
                    self._ball._vx = (-1)*x
                elif self._ball.top - self._ball.height < 0:
                    self._hit_bottom()
                elif self._ball.right - self._ball.width < 0:
                    x = self._ball._vx
                    self._ball._vx = (-1)*x
            
                a = self._getCollidingObject()
            
                if a == self._paddle:
                    if self._ball.vy >0:
                        pass
                    elif self._ball.vy <0:
                        y = self._ball.vy
                        self._ball.vy = (-1)*y
                elif a ==None:
                    pass
                else:
                    self._bricks.remove(a)
                    self.view.remove(a)
                    y = self._ball.vy
                    self._ball.vy = (-1)*y
                
                self._lose_win()
            else:
                pass
    
    def _lose_win(self):
        """ Checks whether the game is compelete and whether the
        player wins or loses.
        
        If there is no bricks left, the player wins. This method
        displays a congratulation message and the game state is
        set to STATE_COMPLETE. If there is no life left, the
        player loses. This method displays an ending message
        and the game state is set to STATE_COMPLETE."""
        
        if len(self._bricks) == 0:
            congrats = GLabel(text= 'Congratulations! YOU WIN!', font_size = 30)
            self.view.add(congrats)
            self._state = STATE_COMPLETE
        elif self._lives == 0:
            lose = GLabel(center_x=GAME_WIDTH/2,center_y=GAME_HEIGHT/2,valign = 'middle', halign = 'center', text = 'GAME OVER', font_size = 30)
            self.view.add(lose)
            self._state = STATE_COMPLETE
        else:
            pass
    
    
    def _hit_bottom(self):
        """ This method is called when the ball goes off the bottom.
        
        It sets the game state to STATE_PAUSED and removes the ball
        object from the view. Because going off the bottom counts as
        losing one life, so this method substracts one life out of
        three. Display a message that informs players the next ball
        is coming up in three seconds.It will wait three seconds for
        the player to prepare for a new ball before serving again."""
        
        self._state = STATE_PAUSED
        self.view.remove(self._ball)
        self._lives = self._lives -1
        message = GLabel(center_x=GAME_WIDTH/2,center_y=GAME_HEIGHT/2,valign = 'middle', halign = 'center',text='Next Ball Coming In 3 Seconds',font_size=15)
        self.view.add(message)
        c = Caller(self.view.remove)
        self.delay(c.remove(message),2.0)
        self.delay(self.serve, 3.0)

    def _getCollidingObject(self):
        """Returns: GObject that has collided with the ball
    
        This method checks the four corners of the ball, one at a 
        time. If one of these points collides with either the paddle 
        or a brick, it stops the checking immediately and returns the 
        object involved in the collision. It returns None if no 
        collision occurred."""
        
        counter = 0
        x = self._ball.x
        y = self._ball.y
        d = BALL_DIAMETER
        
        while counter < len(self._bricks):
            b = self._bricks[counter]
            
            if b.collide_point(x, y) == True:
                return self._bricks[counter]
            else:
                if b.collide_point(x, y+d) == True:
                    return self._bricks[counter]
                else:
                    if b.collide_point(x+d, y+d) == True:
                        return self._bricks[counter]
                    else:
                        if b.collide_point(x+d, y) == True:
                            return self._bricks[counter]
                        else:
                            counter = counter +1
        
        if self._paddle.collide_point(x,y) == True:
            return self._paddle
        else:
            if self._paddle.collide_point(x,y+d) == True:
                return self._paddle
            else:
                if self._paddle.collide_point(x+d,y+d) == True:
                    return self._paddle
                else:
                    if self._paddle.collide_point(x+d,y) == True:
                        return self._paddle
        
        return None
    
    
    def serve(self):
        """ This method is called whenever the game needs to serve or create a new ball.
        
        If the game state is not STATE_COMPLETE, this method creates a new object of class
        Ball, stores it in field _ball, sets the game state to STATE_ACTIVE, and starts the
        ball at the center of the window"""
        
        if self._state != STATE_COMPLETE:
            b = Ball(height = BALL_DIAMETER, width = BALL_DIAMETER)
            self._ball = b
            self._state = STATE_ACTIVE
            b.center_x = GAME_WIDTH/2
            b.center_y = GAME_HEIGHT/2
            self.view.add(b)

    def on_touch_down(self,view,touch):
        """Respond to the mouse (or finger) being pressed (but not released)

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should
        check if the user clicked inside the paddle and begin movement of the
        paddle.  Otherwise, if it is one of the other states, it moves to the
        next state as appropriate.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        # IMPLEMENT ME
        if(self._state == STATE_INACTIVE):
            self._state = STATE_PAUSED
            self.view.remove(self.press_label)
            self._brickMaker()
            self._paddle = GRectangle(pos=(GAME_WIDTH/2 - PADDLE_WIDTH/2, PADDLE_OFFSET),size=(PADDLE_WIDTH,PADDLE_HEIGHT))
            self.view.add(self._paddle)
        elif(self._state == STATE_PAUSED or self._state == STATE_ACTIVE):
            if self._paddle.collide_point(touch.x,touch.y) == True:
                self._state = STATE_ACTIVE
                self._state_active = True
                self._prev_mouse = touch.x
                self._dist = touch.x - self._paddle.x
                self.on_touch_move(view,touch)
                self.delay(self.serve, 3.0)
    
    def _brickMaker(self):
        """Helper function for on_touch_down that creates all the bricks according
        to the constants of the controller class

        Creates all the bricks and appends them to list _bricks as well as adds
        them to the view.

        Precondition: No parameters, returns nothing."""
        x = 0
        clr_counter = 0
        
        #Make all the bricks
        for x in range(BRICK_ROWS):
            y = 0
            for y in range(BRICKS_IN_ROW):
                #Create blocks
                z = GRectangle(pos=(BRICK_SEP_H/2+(BRICK_WIDTH+BRICK_SEP_H)*y, GAME_HEIGHT-(BRICK_Y_OFFSET+(BRICK_HEIGHT+BRICK_SEP_V)*x)),size=(BRICK_WIDTH,BRICK_HEIGHT))
                
                #Increment clr_counter
                if (x != 0 and x%2 == 0 and y == 0):#Every two lines increment clr_counter
                    clr_counter = clr_counter+1
                    if (clr_counter > 4):#If clr_counter exceeds 4, reset to 0
                        clr_counter = 0
                
                #Color Blocks
                if (clr_counter == 0):
                    z.fillcolor = colormodel.RED
                    z.linecolor = colormodel.RED
                elif (clr_counter == 1):
                    z.fillcolor = colormodel.ORANGE
                    z.linecolor = colormodel.ORANGE
                elif (clr_counter == 2):
                    z.fillcolor = colormodel.YELLOW
                    z.linecolor = colormodel.YELLOW
                elif (clr_counter == 3):
                    z.fillcolor = colormodel.GREEN
                    z.linecolor = colormodel.GREEN
                elif (clr_counter == 4):
                    z.fillcolor = colormodel.CYAN
                    z.linecolor = colormodel.CYAN
                
                #Add blocks to _bricks list and view
                self._bricks.append(z)
                self.view.add(z)
    
    def on_touch_move(self,view,touch):
        """Respond to the mouse (or finger) being moved.

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should move
        the paddle. The distance moved should be the distance between the
        previous touch event and the current touch event. For all other
        states, this method is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        # IMPLEMENT ME
        if (self._state == STATE_ACTIVE and self._state_active == True):
            if (self._paddle.x < 0):
                self._paddle.x = 0
            elif (self._paddle.right > GAME_WIDTH):
                self._paddle.x = GAME_WIDTH - PADDLE_WIDTH
            else:
                self._paddle.x = touch.x - self._dist
        else:
            pass

    def on_touch_up(self,view,touch):
        """Respond to the mouse (or finger) being released.

        If state is STATE_ACTIVE, then this method should stop moving the
        paddle. For all other states, it is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        # IMPLEMENT ME
        if (self._state == STATE_ACTIVE):
            self._state_active = False

    # ADD MORE HELPER METHODS (PROPERLY SPECIFIED) AS NECESSARY


class Ball(GEllipse):
    """Instance is a game ball.

    We extends GEllipse because a ball does not just have a position; it
    also has a velocity.  You should add a constructor to initialize the
    ball, as well as one to move it.

    Note: The ball does not have to be a GEllipse. It could be an instance
    of GImage (why?). This change is allowed, but you must modify the class
    header up above."""
    # FIELDS.  You may wish to add properties for them, but that is optional.

    # Velocity in x direction.  A number (int or float)
    _vx = 0.0
    # Velocity in y direction.  A number (int or float)
    _vy = 0.0
    
    # ADD MORE FIELDS (INCLUDE INVARIANTS) AS NECESSARY
    @property
    def vx (self):
        """ x coordinate of the object's velocity.
        
        Immutable. Its value is randomly chosen."""
        
        return self._vx
    
    @property
    def vy (self):
        """ y coordinate of the object's velocity.
        
        Mutable. If it is an int, convert it into a float.
        
        **Invariant**: float or int""" 
        
        return self._vy
    
    @vy.setter
    def vy (self, value):
        assert type(value) == float or int
        
        if type(value) == int:
            value = float(value)
        
        self._vy = value
    
    # ADD MORE METHODS (PROPERLY SPECIFIED) AS NECESSARY

    def __init__(self,**keywords):
        """ **Constructor**: creates a new Ball object.
        
        :param keywords: dictionary of keyword arguments 
            **Precondition**: See below.
        
        To use the constructor for this class, you should provide
        it with a list of keyword arguments that initialize various
        attributes. 
        
        This class supports the same keywords as `GObject`, as well
        as additional attributes for the text properties (e.g. vy)."""
        
        super(Ball, self).__init__(**keywords)
        self._vx = random.uniform(1.0,5.0) 
        self._vx = self._vx * random.choice([-1, 1])
        self.vy = -5.0
        if 'vy' in keywords:
            self.vy = keywords['vy']
        
    
    

# ADD MORE CLASSES AS NECESSARY
