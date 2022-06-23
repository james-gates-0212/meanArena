# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the candidate move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

import world
import random
import utils
from utils import Directions, Pose
class Tallon():

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can
        # query the state of the world
        self.gameWorld = arena

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

    def filterPoses(self, poses, blockPoses):
        filtered = []
        for pose in poses:
            if not utils.containedIn(pose, blockPoses):
                filtered.append(pose)
        return filtered

    def maxSeparationPose(self, poses, targets):
        if len(poses) == 0 or len(targets) == 0:
            return False
        sepas = []
        for pose in poses:
            sepa = 0
            for target in targets:
                sepa += utils.separation(pose, target)
            sepas.append(sepa)
        return poses[sepas.index(max(sepas))]

    # Generate all poses for moving in the world
    def availablePoses(self, poses, target = False):
        candidatePoses = []
        offsets =  [
            { 'x': 0, 'y': +1 }, # North
            { 'x': 0, 'y': -1 }, # South
            { 'x': +1, 'y': 0 }, # Eest
            { 'x': -1, 'y': 0 }, # West
        ]
        for pose in poses:
            for offset in offsets:
                candidatePose = Pose();
                candidatePose.x = pose.x + offset['x']
                candidatePose.y = pose.y + offset['y']
                if (
                    target != False and
                    ( pose.x == target.x or pose.y == target.y )
                ):
                    candidatePose.x = self.gameWorld.reduceDifference(pose.x, target.x)
                    candidatePose.y = self.gameWorld.reduceDifference(pose.y, target.y)
                candidatePose.x = utils.checkBounds(self.gameWorld.maxX, candidatePose.x)
                candidatePose.y = utils.checkBounds(self.gameWorld.maxY, candidatePose.y)
                candidatePoses.append(candidatePose)
        return candidatePoses

    def blockPoses(self, pose = False, noCandidate = False):
        # Get the location of the Meanies.
        allMeanies = self.gameWorld.getMeanieLocation()
        # Get the location of the Pits.
        allPits = self.gameWorld.getPitsLocation()
        allMeaniesCandidatePoses = []
        if not noCandidate:
            allMeaniesCandidatePoses = self.availablePoses(allMeanies, pose)
        return allPits + allMeanies + allMeaniesCandidatePoses

    def candidatePoses(self, pose = False):
        # Filter the available poses to avoid the Pits, Meanies and Meanies's candidate poses
        candidatePoses = self.filterPoses(self.availablePoses([pose]), self.blockPoses(pose))

        return candidatePoses

    def targetMaxPose(self, pose):
        # Get the location of the Meanies.
        allMeanies = self.gameWorld.getMeanieLocation()

        return self.maxSeparationPose(self.candidatePoses(pose), allMeanies)

    def offset(self, pose, offsetX = 0, offsetY = 0):
        newPose = Pose()
        newPose.x = utils.checkBounds(self.gameWorld.maxX, pose.x + offsetX)
        newPose.y = utils.checkBounds(self.gameWorld.maxY, pose.y + offsetY)
        return newPose

    def direction(self, current, target, blocks = []):
        # If not at the same x coordinate, reduce the difference
        if target.x > current.x and not utils.containedIn(self.offset(current, +1, 0), blocks):
            return Directions.EAST
        if target.x < current.x and not utils.containedIn(self.offset(current, -1, 0), blocks):
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if target.y < current.y and not utils.containedIn(self.offset(current, 0, -1), blocks):
            return Directions.NORTH
        if target.y > current.y and not utils.containedIn(self.offset(current, 0, +1), blocks):
            return Directions.SOUTH
        return None

    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Tallon
        # directly towards any existing bonuses. It ignores Meanies
        # and pits.
        #
        # Get the location of the Bonuses.
        allBonuses = self.gameWorld.getBonusLocation()

        # Get the location of the Tallon.
        myCurrentPose = self.gameWorld.getTallonLocation()

        # Found the location of the Meanies.
        foundMeanies = len(self.gameWorld.getMeanieLocation()) > 0

        myTargetPose = self.targetMaxPose(myCurrentPose)

        direction = None

        if foundMeanies and myTargetPose:
            direction = self.direction(myCurrentPose, myTargetPose)

        if direction == None:
            # if there are still bonuses, move towards the candidate one.
            allBlocks = self.blockPoses(myCurrentPose)
            if len(allBonuses) > 0:
                candidateBonus = allBonuses[0]
                direction = self.direction(myCurrentPose, candidateBonus, allBlocks)

        # if there are no more bonuses, Tallon doesn't move
        if direction == None:
            return

        return direction
