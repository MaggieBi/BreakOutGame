# controller.py
# Yunjie Bi (yb89) & Chi Wei Zhang (cz222)
# Dec 3rd, 2012
"""Controller module for Breakout

This module contains a class and global constants for the game Breakout.
Unlike the other files in this assignment, you are 100% free to change
anything in this file. You can change any of the constants in this file
(so long as they are still named constants), and add or remove classes."""

#Extensions: Implemented, sound, replay, and increased collision detection
#to eight points on the ball so that the ball cannot destroy more than one
#brick at a time and to better simulate changing velocity (added changed
#to vx when hitting bricks at certain angles) Also added a
#score label, as well as ball accerlation based on the number of bricks
#destroyed during that life.

import colormodel
import random
from graphics import *
from math import *

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

# Each brick's worth
BRICK_SCORE = 1337
# Life cost
LIFE_COST = 8999

# CLASSES

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
    
    # Boolean to show whether or not the player won
    # Invariant: A boolean
    # Reset on replay
    _winner = False
    
    # Distance between the mouse's x position and the paddle's x
    # Invariant: An int
    # Updates with every click on the paddle
    _dist = 0
    
    # The mouse's previous x position
    # Invariant: A positive int
    # Updates with every click on the paddle
    _prev_mouse = 0
    
    # Whether or not the paddle is in play
    # Invariant: A boolean
    # Changes to True when the paddle is clicked, False when released
    _state_active = False
    
    # The player's game life left
    # Invariant: A positive int in 0 to 3
    # If it is zero, then state is STATE_COMPLETE
    _lives = 3
    
    # The player's score
    # Invariant: An int
    # Increments by BRICK_SCORE as each brick is worth BRICK_SCORE
    _score = 0
    
    # Sounds
    # Sound for collision with paddle or side/top walls
    # Invariant: A .wav sound file
    # Plays when ball hits paddle or side/top walls
    _hit_paddle = Sound('saucer1.wav')
    # Sound for collision with brick
    # Invariant: A .wav sound file
    # Plays when ball hits a brick
    _hit_brick = Sound('cup1.wav')
    # Sound for when ball is served
    # Invariant: A .wav sound file
    # Plays when ball is served
    _serve_sound = Sound('bounce.wav')
    # Sound for when ball hits bottom
    # Invariant: A .wav sound file
    # Plays when ball hits bottom and a life is lost
    _life_lost = Sound('plate1.wav')
    
    # GLabels
    # GLabel for press to play
    # Invariant: A GLabel object
    _press_label = None
    # GLabel for instructions, part A
    # Invariant: A GLabel object
    _instructionsA = None
    # GLabel for instructions, part B
    # Invariant: A GLabel object
    _instructionsB = None
    # GLabel for instructions, part C
    # Invariant: A GLabel object
    _instructionsC = None
    # GLabel for instructions, part D
    # Invariant: A GLabel object
    _instructionsD = None
    # GLabel for the player's score
    # Invariant: A GLabel object
    _score_lab = None
    # GLabel for the number of lives
    # Invariant: A GLabel object
    _lives_lab = None
    # GLabel for replay
    # Invariant: A GLabel object
    _play_again = None
    # GLabel for winning the game
    # Invariant: A GLabel object
    _congrats = None
    # GLabel for losing the game
    # Invariant: A GLabel object
    _lose = None
    # GLabel for ball coming message
    # Invariant: A GLabel object
    _message = None
    
    # METHODS

    def initialize(self):
        """Initialize the game state.

        Initialize any state fields as necessary to statisfy invariants.
        When done, set the state to STATE_INACTIVE, and display a message
        saying that the user should press to play a game."""
        
        self._state = STATE_INACTIVE
        
        #calculate variables for labels
        mid = GAME_WIDTH/2
        top = GAME_HEIGHT-BRICK_Y_OFFSET
        welcome_size = (GAME_WIDTH/21)*1.2
        text_size = welcome_size*.75
        text_div = GAME_HEIGHT/5
        
        #create labels
        self._press_label = GLabel(center_x=mid,center_y=top,
            valign = 'middle', halign = 'center',
            text='~WELCOME TO BREAKOUT~',font_size=welcome_size)
        self._instructionsA = GLabel(center_x=mid,center_y=text_div,
            valign = 'middle', halign = 'center',
            text='Press to Play!',font_size=text_size,
            linecolor = colormodel.RED)
        self._instructionsB = GLabel(center_x=mid,
            center_y=text_div*2,valign = 'middle',
            halign = 'center',text='Drag mouse to move paddle.',
            font_size=text_size,linecolor = colormodel.RED)
        self._instructionsC = GLabel(center_x=mid,center_y=text_div*3,
            valign = 'middle', halign = 'center',
            text='You have 3 lives.',font_size=text_size,
            linecolor = colormodel.RED)
        self._instructionsD = GLabel(center_x=mid,center_y=text_div*4,
            valign = 'middle', halign = 'center',text='Enjoy!',
            font_size=text_size,linecolor = colormodel.RED)
        
        #add labels
        self.view.add(self._press_label)
        self.view.add(self._instructionsA)
        self.view.add(self._instructionsB)
        self.view.add(self._instructionsC)
        self.view.add(self._instructionsD)

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
        
        #if (self._state == STATE_INACTIVE or self._state == STATE_PAUSED or
        #    self._state == STATE_COMPLETE):
        #    pass
        #else:
        if (self._state == STATE_ACTIVE):
            #update position of ball
            if self._ball != None:
                x = self._ball.pos[0]
                y = self._ball.pos[1]
                self._ball.pos = (x + self._ball._vx, y + self._ball.vy)
            
                self._wall_collision()
            
                self._collision()
                
                self._lose_win()
                
            else:
                pass
        else:
            pass

    def on_touch_down(self,view,touch):
        """Respond to the mouse (or finger) being pressed (but not released)

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should
        check if the user clicked inside the paddle and begin movement of the
        paddle.  Otherwise, if it is one of the other states, it moves to the
        next state as appropriate. 

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        
        if(self._state == STATE_INACTIVE):
            #remove labels
            self.view.remove(self._press_label)
            self.view.remove(self._instructionsA)
            self.view.remove(self._instructionsB)
            self.view.remove(self._instructionsC)
            self.view.remove(self._instructionsD)
            
            self._state = STATE_PAUSED
            
            #Set up game
            score_size = BRICK_Y_OFFSET/6
            self._score_lab = GLabel(pos=(score_size,GAME_HEIGHT-score_size*2),
                text='Score:0',font_size=score_size)
            self.view.add(self._score_lab)
            self._lives_lab = GLabel(halign='right',pos=(0,
                GAME_HEIGHT-score_size*2),text='Lives:3',font_size=score_size)
            self._lives_lab.right = GAME_WIDTH-score_size
            self.view.add(self._lives_lab)
            
            self._brick_maker()
            self._paddle = GRectangle(pos=(GAME_WIDTH/2 - PADDLE_WIDTH/2,
                PADDLE_OFFSET),size=(PADDLE_WIDTH,PADDLE_HEIGHT))
            self.view.add(self._paddle)
            self.delay(self._serve, 3.0)
        elif(self._state == STATE_PAUSED or self._state == STATE_ACTIVE):
            #if paddle is clicked, move paddle
            if self._paddle.collide_point(touch.x,touch.y) == True:
                self._state_active = True
                self._prev_mouse = touch.x
                self._dist = touch.x - self._paddle.x
                self.on_touch_move(view,touch)
        elif (self._state == STATE_COMPLETE):
            self._replay()
    
    def on_touch_move(self,view,touch):
        """Respond to the mouse (or finger) being moved.

        If state is STATE_ACTIVE or STATE_PAUSED, then this method should move
        the paddle. The distance moved should be the distance between the
        previous touch event and the current touch event. For all other
        states, this method is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        
        #Move ball in STATE_ACTIVE OR STATE_PAUSED as long as paddle is
        #clicked
        a = touch.x - self._dist
        b = GAME_WIDTH - PADDLE_WIDTH
        
        if ((self._state == STATE_ACTIVE or self._state == STATE_PAUSED)
            and self._state_active == True):
                self._paddle.x = max(min(a, GAME_WIDTH - PADDLE_WIDTH), 0)
        else:
            pass

    def on_touch_up(self,view,touch):
        """Respond to the mouse (or finger) being released.

        If state is STATE_ACTIVE, then this method should stop moving the
        paddle. For all other states, it is ignored.

        Precondition: view is just the view attribute (unused because we have
        access to the view attribute).  touch is a MotionEvent (see
        documentation) with the touch information."""
        
        self._state_active = False

    # ADD MORE HELPER METHODS (PROPERLY SPECIFIED) AS NECESSARY
    def _brick_maker(self):
        """Helper function for on_touch_down that creates all the bricks
        according to the constants of the controller class

        Creates all the bricks and appends them to list _bricks as well as
        adds them to the view."""
        
        x = 0
        clr_counter = 0
        
        #Make all the bricks
        for x in range(BRICK_ROWS):
            y = 0
            for y in range(BRICKS_IN_ROW):
                #Create blocks
                x_pos = BRICK_SEP_H/2+(BRICK_WIDTH+BRICK_SEP_H)*y
                y_pos = (GAME_HEIGHT-(BRICK_Y_OFFSET+
                    (BRICK_HEIGHT+BRICK_SEP_V)*x))
                z = GRectangle(pos=(x_pos,y_pos),
                    size=(BRICK_WIDTH,BRICK_HEIGHT))
                
                #Increment clr_counter
                if (x != 0 and x%2 == 0 and y == 0):
                    clr_counter = clr_counter+1
                    if (clr_counter > 4):
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
    
    def _collision(self):
        """Detects collision with the paddle and the bricks.
        
        If collision is detected with a brick, it updates
        the score and removes the brick and increases
        the ball's speed.  If collision with
        the paddle it inverts the vy of the ball."""
        
        a = self._get_colliding_object()
        #if object is a paddle
        if a == self._paddle:
            self._hit_paddle.play()
            if self._ball.vy >0:
                pass
            elif self._ball.vy <0:
                y = self._ball.vy
                self._ball.vy = (-1)*y
        elif a == None:
            pass
        else:#if object is a brick
            #remove brick and update score and brick list
            self._hit_brick.play()
            self._bricks.remove(a)
            self.view.remove(a)
            self._score = self._score + BRICK_SCORE
            self._score_lab.text = 'Score:' + `self._score`
            #accelerate ball
            if (self._ball._vx < 0):
                self._ball._vx = self._ball._vx - 0.07
                self._ball._vy = self._ball._vy - 0.1
            else:
                self._ball._vx = self._ball._vx + 0.07
                self._ball._vy = self._ball._vy + 0.1
    
    def _wall_collision(self):
        """Detects collision with the walls of the game.
        
        If collision is detected with the ceiling or the
        sides, the ball's vy is inverted. If collision
        is detected with the bottom, then _hit_bottom is
        called."""
        
        if self._ball.top > GAME_HEIGHT:
            self._hit_paddle.play()
            y = self._ball.vy
            self._ball.vy = (-1)*y
        elif self._ball.right > GAME_WIDTH:
            self._hit_paddle.play()
            x = self._ball._vx
            self._ball._vx = (-1)*x
        elif self._ball.top - self._ball.height < 0:
            self._life_lost.play()
            self._hit_bottom()
        elif self._ball.right - self._ball.width < 0:
            self._hit_paddle.play()
            x = self._ball._vx
            self._ball._vx = (-1)*x
    
    def _lose_win(self):
        """ Checks whether the game is compelete and whether the
        player wins or loses.
        
        If there is no bricks left, the player wins. This method
        displays a congratulation message and the game state is
        set to STATE_COMPLETE. If there is no life left, the
        player loses. This method displays an ending message
        and the game state is set to STATE_COMPLETE."""
        
        self._play_again = GLabel(center_x=GAME_WIDTH/2,
            center_y=GAME_HEIGHT/4,valign = 'middle',
            halign = 'center',text='Press to play again.',font_size=15)
        
        #Set Win/Lose complete state and offer replay
        if len(self._bricks) == 0:
            self._congrats = GLabel(text= 'Congratulations! YOU WIN!',
                font_size = 30)
            self.view.add(self._congrats)
            self.view.add(self._play_again)
            self._winner = True
            self._state = STATE_COMPLETE
        elif self._lives == 0:
            self._lose = GLabel(center_x=GAME_WIDTH/2,center_y=GAME_HEIGHT/2,
                valign = 'middle', halign = 'center', text = 'GAME OVER',
                font_size = 30)
            self.view.add(self._lose)
            self.view.add(self._play_again)
            self._loser = True
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
        
        #update lives and deduct points from score
        self._lives = self._lives -1
        self._lives_lab.text = 'Lives:' + `self._lives`
        self._score = self._score - LIFE_COST
        self._score_lab.text = 'Score:' + `self._score`
        
        #Display ball message as long as game is not over
        self._message = GLabel(center_x=GAME_WIDTH/2,center_y=GAME_HEIGHT/2,
            valign = 'middle', halign = 'center',
            text='Next Ball Coming In 3 Seconds',font_size=15)
        if (self._lives != 0):
            self.view.add(self._message)
            self.delay(self._remove,2.0)
            self.delay(self._serve, 3.0)
        else:
            pass
    
    def _remove(self):
        """Helper function for removing message when a new ball is created"""
        
        self.view.remove(self._message)

    def _get_colliding_object(self):
        """Returns: GObject that has collided with the ball
    
        This method checks eight corners of the ball, one at a 
        time. If one of these points collides with either the paddle 
        or a brick, it stops the checking immediately and returns the 
        object involved in the collision. It returns None if no 
        collision occurred."""
        
        #collect returns
        object1 = self._brick_collision()
        object2 = self._paddle_collision()
        
        #return
        if (object1 is not None):
            return object1
        elif (object2 is not None):
            return object2
        else:
            return None
    
    def _brick_collision(self):
        """Returns: GObject that has collided with the ball
    
        This method checks eight corners of the ball, one at a 
        time. If one of these points collides with a brick, it
        stops the checking immediately and returns the 
        object involved in the collision. It returns None if no 
        collision occurred. Depending on the point of collision
        it will change the ball's vy, vx or both."""
        
        counter = 0
        x = self._ball.x
        y = self._ball.y
        d = BALL_DIAMETER
        r = d/2
        #For all the bricks, check collision and
        #change vx/vy appropriately
        while counter < len(self._bricks):
            b = self._bricks[counter]
            if b.collide_point(x, y+d/2) == True:
                self._ball._vx = self._ball._vx * (-1)
                return self._bricks[counter]
            elif b.collide_point(x+d/2, y+d) == True:
                self._ball.vy = self._ball.vy * (-1)
                return self._bricks[counter]
            elif b.collide_point(x+d, y+d/2) == True:
                self._ball._vx = self._ball._vx * (-1)
                return self._bricks[counter]
            elif b.collide_point(x+d/2, y) == True:
                self._ball.vy = self._ball.vy * (-1)
                return self._bricks[counter]
            elif b.collide_point(x+ r- r/sqrt(2), y + r-r/sqrt(2)) == True:
                self._ball._vx = self._ball._vx * (-1)
                self._ball.vy = self._ball.vy * (-1)
                return self._bricks[counter]
            elif b.collide_point(x+ r- r/sqrt(2), y + r+r/sqrt(2)) == True:
                self._ball._vx = self._ball._vx * (-1)
                self._ball.vy = self._ball.vy * (-1)
                return self._bricks[counter]
            elif b.collide_point(x+r+r/sqrt(2), y + r-r/sqrt(2)) == True:
                self._ball._vx = self._ball._vx * (-1)
                self._ball.vy = self._ball.vy * (-1)
                return self._bricks[counter]
            elif b.collide_point(x+r+r/sqrt(2), y+ r+r/sqrt(2)) == True:
                self._ball._vx = self._ball._vx * (-1)
                self._ball.vy = self._ball.vy * (-1)
                return self._bricks[counter]
            else:
                counter = counter +1
        return None
    
    def _paddle_collision(self):
        """Returns: GObject that has collided with the ball
    
        This method checks eight corners of the ball, one at a 
        time. If one of these points collides with the paddle, it
        stops the checking immediately and returns the 
        object involved in the collision. It returns None if no 
        collision occurred."""
        
        x = self._ball.x
        y = self._ball.y
        d = BALL_DIAMETER
        r = d/2
        
        #checks collision with paddle
        if self._paddle.collide_point(x,y+d/2) == True:
            return self._paddle
        elif self._paddle.collide_point(x + d/2,y+d) == True:
            return self._paddle
        elif self._paddle.collide_point(x+d,y+d/2) == True:
            return self._paddle
        elif self._paddle.collide_point(x+d/2,y) == True:
            return self._paddle
        elif self._paddle.collide_point(x+ r- r/sqrt(2),
            y + r-r/sqrt(2)) == True:
            return self._paddle
        elif self._paddle.collide_point(x+ r- r/sqrt(2),
            y + r+r/sqrt(2)) == True:
            return self._paddle
        elif self._paddle.collide_point(x+r+r/sqrt(2),
            y + r-r/sqrt(2)) == True:
            return self._paddle
        elif self._paddle.collide_point(x+r+r/sqrt(2),
            y+ r+r/sqrt(2)) == True:
            return self._paddle
        else:
            return None

    def _serve(self):
        """ This method is called whenever the game needs to serve or create
        a new ball.
        
        If the game state is not STATE_COMPLETE, this method creates a new
        object of class Ball, stores it in field _ball, sets the game state
        to STATE_ACTIVE, and starts the ball at the center of the window"""
        
        #if state does not equal STATE_COMPLETE, create and serve ball
        if self._state != STATE_COMPLETE:
            self._serve_sound.play()
            b = Ball(height = BALL_DIAMETER, width = BALL_DIAMETER)
            self._ball = b
            self._state = STATE_ACTIVE
            self._ball.center_x = GAME_WIDTH/2
            self._ball.center_y = GAME_HEIGHT/2
            self.view.add(self._ball)
    
    def _replay(self):
        """Helper function to clear all the view and set up new game

        Clears all the bricks, messages, paddle, and ball, and 
        Creates all the bricks and appends them to list _bricks as well as
        adds them to the view. Also adds score and lives labels. """
        
        #remove GLabels and objects from view
        self.view.remove(self._ball)
        self.view.remove(self._paddle)
        self.view.remove(self._play_again)
        
        if (self._winner == True):
            self._winner = False
            self.view.remove(self._congrats)
        else:
            self.view.remove(self._lose)
        
        self.view.remove(self._lives_lab)
        self.view.remove(self._score_lab)
        self._lives = 3
        self._score = 0
        
        for x in range(len(self._bricks)):
            y = self._bricks.pop(0)
            self.view.remove(y)
        
        #reset game
        self._state = STATE_PAUSED
        score_size = BRICK_Y_OFFSET/6
        self._score_lab = GLabel(pos=(score_size,GAME_HEIGHT-score_size*2),
            text='Score:0',font_size=score_size)
        self.view.add(self._score_lab)
        self._lives_lab = GLabel(halign='right',pos=(0,
            GAME_HEIGHT-score_size*2),text='Lives:3',font_size=score_size)
        self._lives_lab.right = GAME_WIDTH-score_size
        self.view.add(self._lives_lab)
        self._brick_maker()
        self._paddle = GRectangle(pos=(GAME_WIDTH/2 - PADDLE_WIDTH/2,
            PADDLE_OFFSET),size=(PADDLE_WIDTH,PADDLE_HEIGHT))
        self.view.add(self._paddle)
        self.view.add(self._message)
        self.delay(self._remove,2.0)
        self.delay(self._serve, 3.0)
    

# ADD MORE CLASSES AS NECESSARY
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