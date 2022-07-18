# tallon.py
#
# The code that defines the behaviour of Tallon. This is the place
# (the only place) where you should write code, using access methods
# from world.py, and using makeMove() to generate the candidate move.
#
# Written by: Simon Parsons
# Last Modified: 12/01/22

import config
import world
import random
import utils
from utils import Directions, Pose

config.nonDeterministic = None


class Tallon():

    safeDistance = 0
    allBonuses = []
    currentPose = None
    targetPose = None
    allMeanies = []
    allMeaniesToAvoid = []
    allPits = []

    def __init__(self, arena):

        # Make a copy of the world an attribute, so that Tallon can
        # query the state of the world
        self.gameWorld = arena

        # What moves are possible.
        self.moves = [Directions.NORTH, Directions.SOUTH,
                      Directions.EAST, Directions.WEST]

        # Make the safe distance between Tallon and Meanies
        if config.partialVisibility:
            self.safeDistance = config.visibilityLimit / 2
        else:
            self.safeDistance = config.senseDistance / 2

        # if self.safeDistance < 3:
        #     self.safeDistance = 3

    # Get the poses were not contained the ban poses
    def filterPoses(self, poses, banPoses=[]):
        filtered = []
        for pose in poses:
            if not utils.containedIn(pose, banPoses):
                filtered.append(pose)
        return filtered

    # Get the middle pose in the game world
    def middlePose(self):
        middlePose = Pose()
        middlePose.x = self.gameWorld.maxX / 2
        middlePose.y = self.gameWorld.maxY / 2
        return middlePose

    # Choose the best pose from the given poses by avoiding the Bans and earning the closest Bonus
    def chooseTheBestPose(self, poses, bans=[]):
        if len(poses) == 0 or len(bans) == 0:
            return None

        distances = []
        # Get the closest bonus from Tallon
        bonus = self.closestBonus()
        for pose in poses:
            distance = 0
            for ban in bans:
                # Add the distance between a pose and a ban
                distance += utils.separation(pose, ban)
            if bonus != None:
                # If the closest bonus exists, remove the distance between a pos and a bonus
                # This will make the choosing the closest pose from the given poses
                distance -= utils.separation(pose, bonus)
            distances.append(distance)
        maxDistance = max(distances)

        # Get the candidate poses by the max distance
        candidatePoses = []
        for i in range(len(distances)):
            if distances[i] == maxDistance:
                candidatePoses.append(poses[i])

        # If the candidate pose is only one, will choose this
        if len(candidatePoses) == 1:
            return candidatePoses[0]

        # Otherwise, will choose the closes pose from the middle pose
        middlePose = self.middlePose()

        distances.clear()
        for pose in candidatePoses:
            distance = utils.separation(pose, middlePose)
            for bonus in self.allBonuses:
                distance -= utils.separation(pose, bonus)
            distances.append(distance)

        return candidatePoses[distances.index(min(distances))]

    # Generate all poses for moving in the world
    def availablePoses(self, poses, target=None):
        candidatePoses = []
        # Cross offsets
        offsets = [
            {'x': 0, 'y': +1},  # North
            {'x': 0, 'y': -1},  # South
            {'x': +1, 'y': 0},  # Eest
            {'x': -1, 'y': 0},  # West
        ]
        for pose in poses:
            for offset in offsets:
                candidatePose = Pose()
                candidatePose.x = pose.x + offset['x']
                candidatePose.y = pose.y + offset['y']
                if (
                    target != None and
                    (pose.x == target.x or pose.y == target.y)
                ):
                    candidatePose.x = self.gameWorld.reduceDifference(
                        pose.x, target.x)
                    candidatePose.y = self.gameWorld.reduceDifference(
                        pose.y, target.y)
                candidatePose.x = utils.checkBounds(
                    self.gameWorld.maxX, candidatePose.x)
                candidatePose.y = utils.checkBounds(
                    self.gameWorld.maxY, candidatePose.y)
                candidatePoses.append(candidatePose)
        return candidatePoses

    # Get the dangerous poses from the Pits and Meanies
    def banPoses(self, pose=None, noCandidatePoses=False):
        allMeaniesCandidatePoses = []
        if not noCandidatePoses:
            allMeaniesCandidatePoses = self.availablePoses(
                self.allMeanies, pose)
        return self.allPits + self.allMeanies + allMeaniesCandidatePoses

    # Get the candidate poses from the given pose
    def candidatePoses(self, pose=None):
        if pose == None:
            return []
        # Filter the available poses to avoid the Pits, Meanies and Meanies's candidate poses
        candidatePoses = self.filterPoses(
            self.availablePoses([pose]), self.banPoses(pose))

        return candidatePoses

    # Get the dangerous Meanies in the free distance
    def filterBySafeDistance(self, poses, target):
        filtered = []
        for pose in poses:
            if utils.separation(pose, target) <= self.safeDistance:
                filtered.append(pose)
        return filtered

    # Get the target pose for Tallon to avoid Meanies and earn the closest bonus
    def targetPoseToAvoidMeanies(self):
        self.allMeaniesToAvoid = self.filterBySafeDistance(
            self.allMeanies, self.currentPose)
        self.targetPose = self.chooseTheBestPose(
            self.candidatePoses(self.currentPose), self.allMeaniesToAvoid)

    # Get the pose was moved by offsetX and offsetY from the given pose
    def offset(self, pose, offsetX=0, offsetY=0):
        newPose = Pose()
        newPose.x = utils.checkBounds(self.gameWorld.maxX, pose.x + offsetX)
        newPose.y = utils.checkBounds(self.gameWorld.maxY, pose.y + offsetY)
        return newPose

    # Get the direction between current pose and target pose without ban poses
    def direction(self, bans=[]):
        # If not at the same x coordinate, reduce the difference
        if self.targetPose.x > self.currentPose.x and not utils.containedIn(self.offset(self.currentPose, +1, 0), bans):
            return Directions.EAST
        if self.targetPose.x < self.currentPose.x and not utils.containedIn(self.offset(self.currentPose, -1, 0), bans):
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if self.targetPose.y < self.currentPose.y and not utils.containedIn(self.offset(self.currentPose, 0, -1), bans):
            return Directions.NORTH
        if self.targetPose.y > self.currentPose.y and not utils.containedIn(self.offset(self.currentPose, 0, +1), bans):
            return Directions.SOUTH
        return None

    # Get the direction for travel
    def selfMoveDirection(self):
        direction = self.moves[random.randint(0, 3)]
        # If not at the same x coordinate, reduce the difference
        if direction == Directions.EAST and not utils.containedIn(self.offset(self.currentPose, +1, 0), self.allPits):
            return Directions.EAST
        if direction == Directions.WEST and not utils.containedIn(self.offset(self.currentPose, -1, 0), self.allPits):
            return Directions.WEST
        # If not at the same y coordinate, reduce the difference
        if direction == Directions.NORTH and not utils.containedIn(self.offset(self.currentPose, 0, -1), self.allPits):
            return Directions.NORTH
        if direction == Directions.SOUTH and not utils.containedIn(self.offset(self.currentPose, 0, +1), self.allPits):
            return Directions.SOUTH
        return None

    # Get the closest bonus from the Tallon
    def closestBonus(self):
        if len(self.allBonuses) == 0:
            return None

        distances = []
        for bonus in self.allBonuses:
            distances.append(utils.separation(self.currentPose, bonus))

        return self.allBonuses[distances.index(min(distances))]

    def makeMove(self):
        # This is the function you need to define

        # For now we have a placeholder, which always moves Tallon
        # directly towards any existing bonuses. It ignores Meanies
        # and pits.
        #
        # Get the location of the Bonuses.
        self.allBonuses = self.gameWorld.getBonusLocation()

        # Get the location of the Tallon.
        self.currentPose = self.gameWorld.getTallonLocation()

        # Get the location of the Meanies.
        self.allMeanies = self.gameWorld.getMeanieLocation()

        # Get the location of the Pits.
        self.allPits = self.gameWorld.getPitsLocation()

        self.targetPoseToAvoidMeanies()

        # Found the Meanies to avoid.
        foundMeanies = len(self.allMeaniesToAvoid) > 0

        direction = None

        if foundMeanies and self.targetPose:
            direction = self.direction()

        if direction == None:
            # if there are still bonuses, move towards the candidate one.
            allBans = self.banPoses(self.currentPose)
            if len(self.allBonuses) > 0:
                self.targetPose = self.closestBonus()
                direction = self.direction(allBans)

        # if there are no meanies to avoid and no candidate bonus, Tallon travels itself.
        if not foundMeanies and direction == None:
            direction = self.selfMoveDirection()

        # if there are no meanies to avoid and no more bonus, Tallon doesn't move
        if direction == None:
            return

        return direction
