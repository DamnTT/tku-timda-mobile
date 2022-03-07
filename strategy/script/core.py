#!/usr/bin/env python
from yaml import serialize
import rospy
import sys
import math
import time
from robot.robot import Robot
from qga import Qga
from my_sys import log, SysCheck, logInOne
from dynamic_reconfigure.server import Server as DynamicReconfigureServer
from strategy.cfg import RobotConfig
import dynamic_reconfigure.client
from std_msgs.msg import String
from std_msgs.msg import Int32
from actionlib_msgs.msg import GoalID
from diagnostic_msgs.srv import AddDiagnostics, AddDiagnosticsResponse
import itertools
from strategy.srv import TimdaMode, TimdaModeResponse
#from strategy.srv import arucoRelativePose, arucoRelativePoseResponse
from strategy.msg import TimdaMobileStatus
ADJUST = "Timda_mobile_relative_pose"
TIMDA_SERVER = "Timda_mobile"
CUSTOMER = "customer_order"
TIMDA_STATUS = "timda_mobile_status"


class Core(Robot, Qga):
    def Callback(self, config, level):
        self.gameStart = config['GAME_START']
        self.getLoc = config['LOC_GET']
        self.mode = config['ROBOT_MODE']
        self.item = config['ITEM']
        self.navMode = config['NAV_MODE']
        self.navStart = config['NAV_START']
        self.locReset = config['LOC_RESET']
        self.yamlLoad = config['YAML_LOAD']
        self.saveYaml = config['YAML_SAVE']

        return config

    def __init__(self, sim=False):
        # super(Core, self).__init__(sim)
        Robot.__init__(self, sim)
        # Qga.__init__(self, sim)
        print("fuck end")
        self.initialPoint = self.loc

        dsrv = DynamicReconfigureServer(RobotConfig, self.Callback)


class Strategy(object):

    def __init__(self, sim=False):
        rospy.init_node('core', anonymous=False)
        self.rate = rospy.Rate(200)
        self.robot = Core(sim)
        self.dclient = dynamic_reconfigure.client.Client(
            "core", timeout=30, config_callback=None)
        self.dclient.update_configuration(
            {"GAME_START": False,
             "ROBOT_MODE": "idle",
             "NAV_START": "False"})
        self.calList = []
        self.tableNum = []
        self.serviceList = []
        self.stop = GoalID()
        rospy.Service(TIMDA_SERVER, TimdaMode, self.handleTimdaMobile)
        #rospy.Service(ADJUST, aruco_relative_pose, self.adjustTimda)
        rospy.Service(CUSTOMER, AddDiagnostics, self.web_customer)
        self.publishStatus = self.robot._Publisher(
            TIMDA_STATUS,  TimdaMobileStatus)

        self.main()

#--------------------------------------------------------------------------------------------------------#
# main Strategy
#--------------------------------------------------------------------------------------------------------#
    def main(self):
        while not rospy.is_shutdown():
            if self.robot.gameStart == True:
                if self.robot.mode == "Navigating":
                    if self.robot.navStart == True:
                        print("Navigate to " + self.robot.item)
                        a = self.robot.goalClient(self.robot.item)
                        print(a)
                        while 1:
                            if self.robot.status[0].status == 3:
                                print("Nav Stop")
                                print(self.robot.item + " Reached!")
                                break
                            elif self.robot.status[0].status == 5 or self.robot.status[0].status == 4 or self.robot.status[0].status == 6 or self.robot.status[0].status == 7 or self.robot.status[0].status == 2:
                                print("Nav Cancel!")
                                break
                        while self.robot.navMode == "directory":
                            if self.robot.navStart == False:
                                break
                        self.dclient.update_configuration(
                            {"NAV_START": "False"})
                        self.dclient.update_configuration(
                            {"ROBOT_MODE": "Idle"})

                elif self.robot.mode == "Setting":
                    if self.robot.getLoc == True:
                        print("it is setting " + self.robot.item + "position")
                        self.robot.recordPosition(self.robot.item)
                        self.dclient.update_configuration({"LOC_GET": "False"})
                    elif self.robot.locReset == True:
                        print("it is reset " + self.robot.item, " location")
                        self.robot.resetLocation(self.robot.item)
                        self.dclient.update_configuration(
                            {"LOC_RESET": "False"})

                elif self.robot.mode == "test":
                    arr = self.robot.calculate(True)
                    print("final:"+arr)

                    self.dclient.update_configuration(
                        {"ROBOT_MODE": "Idle"})
                    # self.test()

                if self.robot.yamlLoad == True:
                    self.robot.loadYaml()
                    self.dclient.update_configuration(
                        {"YAML_LOAD": "False"})
                elif self.robot.saveYaml == True:
                    self.robot.getYaml()
                    self.dclient.update_configuration(
                        {"YAML_SAVE": "False"})
            else:
                self.dclient.update_configuration(
                    {
                        "ROBOT_MODE": "idle",
                        "NAV_START": "False",
                        "LOC_GET": False,
                        "LOC_RESET": False,
                        "YAML_SAVE": False,
                        "YAML_LOAD": False
                    })

#--------------------------------------------------------------------------------------------------------#
# Service function
#--------------------------------------------------------------------------------------------------------#

    def test(self):
        print("""QUANTUM GENETIC ALGORITHM""")
        # f = open(
        #     "/home/damn/timda-mobile/src/strategy/script/timda-advance/output.dat", "w")
        # # fi = open("output_2.dat", "w")
        # fi3 = open(
        #     "/home/damn/timda-mobile/src/strategy/script/best_result.dat", "w")

        # input("Press Enter to continue...")
        # selot.Init_sample()
        print("QGA result is :", self.robot.Q_GA())
        # fi3 = open(
        #     "/home/damn/timda-mobile/src/strategy/script/best_result.dat", "a")
        # # f.write(str(generation)+" "+str(fitness_average)+"\n")
        # fi3.write(str(i)+" "+str(max)+"\n")
        # fi3.write(" \n")
        # fi3.close()
        # Init_population()
        # print(rt)
        self.robot.plot_Output()
        self.dclient.update_configuration({"ROBOT_MODE": "Idle"})

    def handleTimdaMobile(self, req):
        res = TimdaModeResponse()
        if self.robot.mode == "Service":
            item_key = list(self.robot.item_dict.keys())

            if item_key.count(req.item_req) > 0:
                self.dclient.update_configuration({"Item": req.item_req})
                self.dclient.update_configuration({"navStart": "True"})
                print("Navigation to" + self.robot.item)
                if self.robot.navStart == True:
                    a = self.robot.goalClient(self.robot.item)
                    print(a)
                    while 1:
                        if self.robot.status[0].status == 3:
                            print("Nav Stop")
                            print(req.item_req + "Reached!")
                            break
                        elif self.robot.status[0].status == 5 or self.robot.status[0].status == 4 or self.robot.status[0].status == 6 or self.robot.status[0].status == 7 or self.robot.status[0].status == 2:
                            print("Nav Cancel!")
                            break

                    while self.robot.navMode == "directory":
                        if self.robot.navStart == False:
                            break
                    self.dclient.update_configuration(
                        {"NAV_START": "False"})
                res.nav_res = 'finish'
            elif self.robot.item_adjust.count(req.item_req) > 0:
                loc = self.robot.loc
                var = 0.2
                varo = 0.27
                limR = 0.1
                limV = 0.1
                while 1:
                    if "back" in req.item_req:
                        disX = (loc.pose.pose.position.x - var) - \
                            self.robot.loc.pose.pose.position.x
                        disY = 0
                        if abs(disX) < limR:
                            self.robot.RobotCtrlS(0, 0, 0)
                            res.nav_res = 'finish'
                            print("Move Stop")
                            break
                        self.robot.RobotCtrlS(limV * -1, 0, 0)
                    elif "front" in req.item_req:
                        disX = (loc.pose.pose.position.x + var) - \
                            self.robot.loc.pose.pose.position.x
                        disY = 0
                        if abs(disX) < limR:
                            self.robot.RobotCtrlS(0, 0, 0)
                            res.nav_res = 'finish'
                            break
                        self.robot.RobotCtrlS(limV, 0, 0)
                    elif "left" in req.item_req:
                        disX = 0
                        disY = (loc.pose.pose.position.y + varo) - \
                            self.robot.loc.pose.pose.position.y
                        if abs(disY) < limR:
                            self.robot.RobotCtrlS(0, 0, 0)
                            res.nav_res = 'finish'
                            break
                        self.robot.RobotCtrlS(0, limV, 0)
                    elif "right" in req.item_req:
                        disX = 0
                        disY = (loc.pose.pose.position.y - varo) - \
                            self.robot.loc.pose.pose.position.y

                        if abs(disY) < limR:
                            self.robot.RobotCtrlS(0, 0, 0)
                            res.nav_res = 'finish'
                            break
                        self.robot.RobotCtrlS(0, limV * -1, 0)

                print("Move Stop")
        else:
            print(req)
            res.nav_res = 'finish'
        return res

    def web_customer(self, req):
        res = AddDiagnosticsResponse()
        self.publishStatus.publish(req.load_namespace)
        res.message = "Receive Order, Please Wait a minute"
        return res


if __name__ == '__main__':
    try:
        if SysCheck(sys.argv[1:]) == "Native Mode":
            log("Start Native")
            s = Strategy(False)
        elif SysCheck(sys.argv[1:]) == "Simulative Mode":
            log("Start Sim")
            s = Strategy(True)
            # Initializes a rospy node so that the SimpleActionClient can
            # publish and subscribe over ROS.
            # print "Result:", ', '.join([str(n) for n in result.sequence])
    except rospy.ROSInterruptException:
        print("program interrupted before completion")
        pass
