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
        self.loc = PoseWithCovarianceStamped()
        self.calculate_path = False
        self.Current_loc = PoseWithCovarianceStamped()
        self.initial_point = PoseWithCovarianceStamped()
        self.status = []  # waiting
        self.item_dict = {}
        self.cal_list = []
        self.tableNum = []
        self.item_adjust = []
        self.path = Path()
        rospy.Subscriber(
            "amcl_pose", PoseWithCovarianceStamped, self._getPosition)
        rospy.Subscriber("move_base/status", GoalStatusArray, self._getstatus)
        self.path_subscriber = rospy.Subscriber(
            "move_base/NavfnROS/plan", Path, self._getPath)
        self.pub_goal = self._Publisher(GOAL_TOPIC, PoseStamped)
        self.pub_initial_point = self._Publisher(
            INITIALPOSE_TOPIC, PoseWithCovarianceStamped)
        self.pub_stopNav = self._Publisher(
            GOAL_STOP_TOPIC, GoalID)
        self.cmdvel_pub = self._Publisher(MOBILE_CMD_VEL, Twist)

#--------------------------------------------------------------------------------------------------------#
# Navigation function
#--------------------------------------------------------------------------------------------------------#

    def adjust_mobile_list(self, name):
        adjust_back = name + "_back"
        adjust_front = name + "_front"
        adjust_right = name + "_right"
        adjust_left = name + "_left"
        self.item_adjust.append(adjust_back)
        self.item_adjust.append(adjust_front)
        self.item_adjust.append(adjust_left)
        self.item_adjust.append(adjust_right)

    def RobotCtrlS(self, output_x, output_y, yaw, pass_through=False):
        if pass_through:
            msg = Twist()
            # output_x, output_y = self.Rotate(x, y, ROTATE_V_ANG)
            msg.linear.x = output_x
            msg.linear.y = output_y
            msg.angular.z = yaw
            print(output_x, output_y, yaw)
            self.cmdvel_pub.publish(msg)
        else:

            msg = Twist()

            msg.linear.x = output_x
            msg.linear.y = output_y

            msg.angular.z = 0
            self.cmdvel_pub.publish(msg)

    def goal_client(self, goal):
        # Creates the SimpleActionClient, passing the type of the action
        self.client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
        # Waits until the action server has started up and started
        # listening for goals.
        self.client.wait_for_server()
        goal_tmp = self.item_dict[goal]

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
        self.pub_initial_point.publish(self.item_dict[name])
        print(name, "Reset done")

    def recordPosition(self, name):
        # if cmd == 1:
        if name == "Current":
            self.Current_loc = self.loc
        # elif name == "initial":
        #     self.initial_point = self.loc
        else:
            self.item_dict[name] = self.loc
            self.adjust_mobile_list(name)
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
            self.pub_stopNav.publish(GoalID())
            self.path = path
        else:
            pass

    def _getstatus(self, mobilestatus):
        self.status = mobilestatus.status_list


#--------------------------------------------------------------------------------------------------------#
# Getting information
#--------------------------------------------------------------------------------------------------------#


    def GetPath(self):
        return self.path

    def Getstatus(self):
        return self.status

    def GetCal_list(self):
        cal_list = []

        for i in self.item_dict:
            cal_list.append(self.item_dict[i])
        return cal_list

    def GetTable(self):

        table_tmp = self.tableNum(0)

    def GetYaml(self):
        file = open('position.yaml', mode='w')
        yaml.dump(self.item_dict, file, encoding=('utf-8'))
        file.close()
        print("YAML create finished")

    def LoadYaml(self):
        with open("position.yaml", 'r') as stream:
            self.item_dict = yaml.load(stream, Loader=yaml.CLoader)
        print("YAML load success!")
#--------------------------------------------------------------------------------------------------------#
# Calculate route function
#--------------------------------------------------------------------------------------------------------#

    def Calculate(self, cmd):
        if cmd == True:
            self.calculate_path = True
        else:
            self.pub_initial_point.publish(self.Current_loc)
            self.calculate_path = False

    def setting_path_point(self, str, kk, start_point, goal_point):
        self.start_point = PoseWithCovarianceStamped()
        self.start_point.pose.pose.position.x = start_point.pose.pose.position.x
        self.start_point.pose.pose.position.y = start_point.pose.pose.position.y
        self.start_point.header.stamp = rospy.Time.now()
        self.start_point.pose.pose.orientation.z = start_point.pose.pose.orientation.z
        self.start_point.pose.pose.orientation.w = start_point.pose.pose.orientation.w
        self.start_point.header.frame_id = 'map'
        rospy.sleep(1)
        self.pub_initial_point.publish(self.start_point)
        print(str, kk, "Start Point sends sucessfull ")
        print("--------------------")
        self.goal_point = PoseStamped()
        self.goal_point.pose.position.x = goal_point.pose.pose.position.x
        self.goal_point.pose.position.y = goal_point.pose.pose.position.y
        self.goal_point.header.stamp = rospy.Time.now()
        self.goal_point.pose.orientation.z = goal_point.pose.pose.orientation.z
        self.goal_point.pose.orientation.w = goal_point.pose.pose.orientation.w
        self.goal_point.header.frame_id = 'map'
        rospy.sleep(2)
        self.pub_goal.publish(self.goal_point)
        print(str, kk, "Goal Point sends sucessfull")
        print("--------------------")
        print("Listening to " + "move_base/NavfnROS/plan")
        rospy.wait_for_message("move_base/NavfnROS/plan", Path)

    def PrintPath(self, path):
        # global subscriber
        first_time = True
        prev_x = 0.0
        prev_y = 0.0
        total_distance = 0.0
        if len(path.poses) > 0:
            for current_point in path.poses:
                x = current_point.pose.position.x
                y = current_point.pose.position.y
                if not first_time:
                    total_distance += math.hypot(prev_x - x, prev_y - y)
                else:
                    first_time = False
                prev_x = x
                prev_y = y
        return total_distance
