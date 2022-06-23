# utils.py
#
# Some bits and pieces that are used in different places in the Mean Arena
# world code.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

import random
import math
from enum import Enum

# Representation of directions
class Directions(Enum):
    NORTH = 0
    SOUTH = 1
    EAST  = 2
    WEST  = 3

# representation of game state
class State(Enum):
    PLAY = 0
    WON  = 1
    LOST = 2

# Class to represent the position of elements within the game
#
class Pose():
    x = 0
    y = 0

    def print(self):
        print('[', self.x, ',', self.y, ']')

# Check if two game elements are in the same location
def sameLocation(pose1, pose2):
    if pose1.x == pose2.x:
        if pose1.y == pose2.y:
            return True
        else:
            return False
    else:
        return False

# Return distance between two game elements.
def separation(pose1, pose2):
    return math.sqrt((pose1.x - pose2.x) ** 2 + (pose1.y - pose2.y) ** 2)

# Make sure that a location doesn't step outside the bounds on the world.
def checkBounds(max, dimension):
    if (dimension > max):
        dimension = max
    if (dimension < 0):
        dimension = 0

    return dimension

# Pick a location in the range [0, x] and [0, y]
#
# Used to randomize the initial conditions.
def pickRandomPose(x, y):
    p = Pose()
    p.x = random.randint(0, x)
    p.y = random.randint(0, y)

    return p

# Pick a unique location, in the range [0, x] and [0, y], given a list
# of locations that have already been chosen.

def pickUniquePose(x, y, taken):
    uniqueChoice = False
    while(not uniqueChoice):
        candidatePose = pickRandomPose(x, y)
        # Don't seem to be able to use 'in' here. I suspect it is
        # because of the way __contains__ checks for equality.
        if not containedIn(candidatePose, taken):
            uniqueChoice = True
    return candidatePose

# Check if a pose with the same x and y is already in poseList.
#
# There should be a way to do this with in/__contains__ by overloading
# the relevant equality operator for pose, but that is for another
# time.
def containedIn(pose, poseList):
    contained = False
    for poses in poseList:
        if sameLocation(pose, poses):
            contained = True
            #print(pose, "and", poses, "are (both) at (", pose.x, ",", pose.y, ") and (", pose.x, ", ", pose.y, ")")
    return contained

# Print out game state information. Not so useful given the graphical
# display, but might come in handy. Note that what is printed is
# Tallon's view --- that is it imposes the visbility limit relative to
# Tallon. To get the full view, remove the visibility limit.
def printGameState(world):
    print("Meanies:")
    for i in range(len(world.getMeanieLocation())):
        world.getMeanieLocation()[i].print()
        
    print("Tallon:")
    world.getTallonLocation().print()

    print("Bonuses:")
    for i in range(len(world.getBonusLocation())):
        world.getBonusLocation()[i].print()

    print("Pits:")
    for i in range(len(world.getPitsLocation())):
        world.getPitsLocation()[i].print()

    print("Clock:")
    print(world.getClock())

    print("Score:")
    print(world.getScore())

    print("")
