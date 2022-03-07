#!/usr/bin/env python

import os
import math
import actionlib
import rospy
import sys
import roslib
import numpy as np
import yaml
from actionlib_msgs.msg import GoalID
from actionlib_msgs.msg import GoalStatusArray
from move_base_msgs.msg import MoveBaseActionGoal
from move_base_msgs.msg import MoveBaseAction
from move_base_msgs.msg import MoveBaseGoal
from geometry_msgs.msg import PoseStamped, Twist
from geometry_msgs.msg import PoseWithCovarianceStamped
from nav_msgs.msg import Path
from std_msgs.msg import Int32
from std_msgs.msg import String
from itertools import permutations


roslib.load_manifest('move_base')

# Brings in the SimpleActionClient

# Brings in the messages used by the fibonacci action, including the
# goal message and the result message.


POS_RECORD_TOPIC = "pos_record"
PATH_CALCULATE_TOPIC = ""
GOAL_TOPIC = "move_base_simple/goal"
INITIALPOSE_TOPIC = "initialpose"
GOAL_STOP_TOPIC = "move_base/cancel"
MOBILE_CMD_VEL = "mobile/cmd_vel"
subscriber = None


class Robot(object):

    # Configs

    def __init__(self, sim=False):
        print("fuxk")
        self.loc = PoseWithCovarianceStamped()
        self.calculate_path = False
        self.currentLoc = PoseWithCovarianceStamped()
        self.initialPoint = PoseWithCovarianceStamped()
        self.status = []  # waiting
        self.itemDict = {}
        self.calList = []
        self.tableNum = []
        self.itemAdjust = []
        self.arr = "0123"
        self.path = Path()
        rospy.Subscriber(
            "amcl_pose", PoseWithCovarianceStamped, self._getPosition)
        rospy.Subscriber("move_base/status", GoalStatusArray, self._getstatus)
        self.pathSubscriber = rospy.Subscriber(
            "move_base/NavfnROS/plan", Path, self._getPath)
        self.pubGoal = self._Publisher(GOAL_TOPIC, PoseStamped)
        self.pubInitialPoint = self._Publisher(
            INITIALPOSE_TOPIC, PoseWithCovarianceStamped)
        self.pubStopNav = self._Publisher(
            GOAL_STOP_TOPIC, GoalID)
        self.cmdvelPub = self._Publisher(MOBILE_CMD_VEL, Twist)

#--------------------------------------------------------------------------------------------------------#
# Navigation function
#--------------------------------------------------------------------------------------------------------#

    def adjustMobileList(self, name):
        adjustBack = name + "_back"
        adjustFront = name + "_front"
        adjustRight = name + "_right"
        adjustLeft = name + "_left"
        self.itemAdjust.append(adjustBack)
        self.itemAdjust.append(adjustFront)
        self.itemAdjust.append(adjustLeft)
        self.itemAdjust.append(adjustRight)

    def RobotCtrlS(self, outputX, outputY, yaw, passThrough=False):
        if passThrough:
            msg = Twist()
            # outputX, outputY = self.Rotate(x, y, ROTATE_V_ANG)
            msg.linear.x = outputX
            msg.linear.y = outputY
            msg.angular.z = yaw
            print(outputX, outputY, yaw)
            self.cmdvelPub.publish(msg)
        else:

            msg = Twist()

            msg.linear.x = outputX
            msg.linear.y = outputY

            msg.angular.z = 0
            self.cmdvelPub.publish(msg)

    def goalClient(self, goal):
        # Creates the SimpleActionClient, passing the type of the action
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        # Waits until the action server has started up and started
        # listening for goals.
        self.client.wait_for_server()
        goal_tmp = self.itemDict[goal]

        # Creates a goal to send to the action server.
        self.goal = MoveBaseGoal()
        self.goal.target_pose.header.frame_id = "map"
        self.goal.target_pose.header.stamp = rospy.get_rostime()
        self.goal.target_pose.pose.position.x = goal_tmp.pose.pose.position.x
        self.goal.target_pose.pose.position.y = goal_tmp.pose.pose.position.y
        self.goal.target_pose.pose.orientation.z = goal_tmp.pose.pose.orientation.z
        self.goal.target_pose.pose.orientation.w = goal_tmp.pose.pose.orientation.w

        # Sends the goal to the action server.
        rospy.loginfo("Sending goal")
        self.client.send_goal(self.goal)

        # Waits for the server to finish performing the action.
        self.client.wait_for_result()

        # Prints out the result of executing the action
        return self.client.get_result()  # A FibonacciResult

    def resetLocation(self, name):
        self.pubInitialPoint.publish(self.itemDict[name])
        print(name, "Reset done")

    def recordPosition(self, name):
        # if cmd == 1:
        if name == "Current":
            self.currentLoc = self.loc
        # elif name == "initial":
        #     self.initialPoint = self.loc
        else:
            self.itemDict[name] = self.loc
            self.adjustMobileList(name)
        print(name, "Record done")
#--------------------------------------------------------------------------------------------------------#
# Publish function
#--------------------------------------------------------------------------------------------------------#

    def _Publisher(self, topic, mtype):
        return rospy.Publisher(topic, mtype, queue_size=10)
#--------------------------------------------------------------------------------------------------------#
# Subscribe function
#--------------------------------------------------------------------------------------------------------#

    def _getPosition(self, pos):
        self.loc = pos

    def _getPath(self, path):
        if self.calculate_path == True:
            self.pubStopNav.publish(GoalID())
            self.path = path
        else:
            pass

    def _getstatus(self, mobilestatus):
        self.status = mobilestatus.status_list


#--------------------------------------------------------------------------------------------------------#
# Getting information
#--------------------------------------------------------------------------------------------------------#

    def getPath(self):
        return self.path

    def getstatus(self):
        return self.status

    def getcalList(self):
        calList = []

        for i in self.itemDict:
            calList.append(self.itemDict[i])
        return calList

    def getArr(self):

        return self.arr

    def getYaml(self):
        file = open('position.yaml', mode='w')
        yaml.dump(self.itemDict, file, encoding=('utf-8'))
        file.close()
        print("YAML create finished")

    def loadYaml(self):
        with open("position.yaml", 'r') as stream:
            self.itemDict = yaml.load(stream, Loader=yaml.CLoader)
        print("YAML load success!")
#--------------------------------------------------------------------------------------------------------#
# Calculate route function
#--------------------------------------------------------------------------------------------------------#

    def calculate(self, cmd):
        iii = []
        if cmd == True:
            self.recordPosition("Current")
            y = 0
            x = list(permutations(self.arr, 4))
            for i in x:
                print(i)
                y = 0
                for k in range(len(i)):
                    tmp = "0"+i[k]
                    tmp2 = "0"+i[k+1]
                    if k == 0:
                        y = y + \
                            self.settingPathPoint(
                                "initial", tmp, self.itemDict["initial"], self.itemDict[tmp])

                    print(i[k], " plus ", i[k+1])
                    y = y + \
                        self.settingPathPoint(
                            tmp, tmp2, self.itemDict["initial"], self.itemDict[tmp])

                    if (k+1) == len(i)-1:
                        y = y + \
                            self.settingPathPoint(
                                tmp2, "initial", self.itemDict[tmp2], self.itemDict["initial"])
                        break
                iii.append(y)
                print("total:", y)

            print(iii)
            self.pubInitialPoint.publish(self.currentLoc)
        return iii
        # else:
        #     # self.calculate_path = False

    def settingPathPoint(self, str, kk, startPoint, goalPoint):
        self.calculate_path = True
        self.startPoint = PoseWithCovarianceStamped()
        self.startPoint.pose.pose.position.x = startPoint.pose.pose.position.x
        self.startPoint.pose.pose.position.y = startPoint.pose.pose.position.y
        self.startPoint.header.stamp = rospy.Time.now()
        self.startPoint.pose.pose.orientation.z = startPoint.pose.pose.orientation.z
        self.startPoint.pose.pose.orientation.w = startPoint.pose.pose.orientation.w
        self.startPoint.header.frame_id = 'map'
        rospy.sleep(1)
        self.pubInitialPoint.publish(self.startPoint)
        print(str, kk, "Start Point sends sucessfull ")
        print("--------------------")
        self.goalPoint = PoseStamped()
        self.goalPoint.pose.position.x = goalPoint.pose.pose.position.x
        self.goalPoint.pose.position.y = goalPoint.pose.pose.position.y
        self.goalPoint.header.stamp = rospy.Time.now()
        self.goalPoint.pose.orientation.z = goalPoint.pose.pose.orientation.z
        self.goalPoint.pose.orientation.w = goalPoint.pose.pose.orientation.w
        self.goalPoint.header.frame_id = 'map'
        rospy.sleep(2)
        self.pubGoal.publish(self.goalPoint)
        print(str, kk, "Goal Point sends sucessfull")
        print("--------------------")
        print("Listening to " + "move_base/NavfnROS/plan")
        # tmpPath = rospy.wait_for_message("move_base/NavfnROS/plan", Path)
        self.calculate_path = False
        return self.PrintPath(self.path)

    def PrintPath(self, path):
        # global subscriber
        firstTime = True
        prevX = 0.0
        prevY = 0.0
        totalDistance = 0.0
        if len(path.poses) > 0:
            for currentPoint in path.poses:
                x = currentPoint.pose.position.x
                y = currentPoint.pose.position.y
                if not firstTime:
                    totalDistance += math.hypot(prevX - x, prevY - y)
                else:
                    firstTime = False
                prevX = x
                prevY = y
        return totalDistance
