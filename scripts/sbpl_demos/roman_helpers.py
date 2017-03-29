#! /usr/bin/env python
import sys
import rospy
import roslib
import math
import actionlib
import tf
from tf.transformations import quaternion_from_euler
from rcta.msg import MoveArmGoal, MoveArmAction
from geometry_msgs.msg import Pose, PoseStamped
from moveit_msgs.msg import RobotState
from sensor_msgs.msg import JointState
from control_msgs.msg import GripperCommandAction, GripperCommandGoal
from roman_client_ros_utils.msg import RobotiqSimpleCmd, RobotiqActivate

import copy
import moveit_commander
import moveit_msgs.msg


class RomanMoveArm(object):
    def __init__(self):
        self.client=actionlib.SimpleActionClient('/move_arm', MoveArmAction)
        self.tflistener = tf.TransformListener()
        rospy.loginfo("Waiting for action /move_arm...")
        self.client.wait_for_server()
        rospy.loginfo("Connected to action /move_arm!")

    def MoveToHome(self):
        pose = Pose()
        pose.position.x = 0.468
        pose.position.y = -0.767
        pose.position.z = 1.170
        quat = quaternion_from_euler(-math.pi/2,0,0)
        pose.orientation.x = quat[0]
        pose.orientation.y = quat[1]
        pose.orientation.z = quat[2]
        pose.orientation.w = quat[3]
        return self.MoveToPose(pose, "base_footprint")

    def MoveToHandoff(self):
        pose = Pose()
        pose.position.x = 0.531
        pose.position.y = -0.682
        pose.position.z = 1.167
        quat = quaternion_from_euler(math.pi,0,-2.993)
        pose.orientation.x = quat[0]
        pose.orientation.y = quat[1]
        pose.orientation.z = quat[2]
        pose.orientation.w = quat[3]
        return self.MoveToPose(pose, "base_footprint")


    def MoveToPose(self, desired_pose, reference_frame="map"):
        goal=MoveArmGoal()
        '''
        # goal 
        uint8 EndEffectorGoal = 0
        uint8 JointGoal = 1
        uint8 CartesianGoal = 2
        uint8 type
        geometry_msgs/Pose goal_pose
        sensor_msgs/JointState goal_joint_state
        moveit_msgs/RobotState start_state
        octomap_msgs/Octomap octomap
        bool execute_path
        moveit_msgs/PlanningOptions planning_options
        '''

        goal.type = 0 # EEgoal

        if(    not self.tflistener.frameExists(reference_frame) or not self.tflistener.frameExists("map")):
            rospy.logwarn("Warning: could not look up provided reference frame")
            return False
        input_ps = PoseStamped()
        input_ps.pose = desired_pose
        input_ps.header.frame_id = reference_frame
        correct_ps = self.tflistener.transformPose("map", input_ps )

        goal.goal_pose = correct_ps.pose
        rospy.loginfo("sending robot to pose: ")
        print goal.goal_pose
        goal.execute_path = True

        rospy.loginfo("Sending goal to action Server")
        self.client.send_goal(goal)
        result = self.client.wait_for_result()
        rospy.loginfo("Finished pose goal - result is %d", result)
        if result:
            return True
        else:
            return False

class RomanCommandGripper(object):
    def __init__(self):

        self.activate_pub = rospy.Publisher("roman_hand_activate", RobotiqActivate, queue_size=1)
        self.open_pub = rospy.Publisher("roman_hand_open", RobotiqSimpleCmd, queue_size=1)
        self.close_pub = rospy.Publisher("roman_hand_close", RobotiqSimpleCmd, queue_size=1)
        
        

    def Activate(self):
        activate_msg = RobotiqActivate()
        activate_msg.mech = 0 # right
        activate_msg.activate = True
        self.activate_pub.publish(activate_msg)
        print "Commanding Robotiq Active, only need to do this once"
        rospy.sleep(1.0) 

    def Deactivate(self):
        activate_msg = RobotiqActivate()
        activate_msg.mech = 0 # right
        activate_msg.activate = False
        activate_pub.publish(activate_msg)
        print "Commanding Robotiq Deactivate"
        rospy.sleep(1.0) 

    def Close(self):
        #self.activate_pub.publish(self.activate_msg)
        goal=RobotiqSimpleCmd()
        goal.mech = 0 # right
        goal.close = True
        self.close_pub.publish(goal)
        print "Commanding Robotiq Close"
        rospy.sleep(3.0) 

    def Pinch(self):
        #self.activate_pub.publish(self.activate_msg)
        goal=RobotiqSimpleCmd()
        goal.mech = 0 # right
        goal.close = True
        goal.mode = 2
        self.close_pub.publish(goal)
        print "Commanding Robotiq Pinch"
        rospy.sleep(4.0) 

    def Wide(self):
        #self.activate_pub.publish(self.activate_msg)
        goal=RobotiqSimpleCmd()
        goal.mech = 0 # right
        goal.close = True
        goal.mode = 1
        self.close_pub.publish(goal)
        print "Commanding Robotiq Wide"
        rospy.sleep(3.0)

    def Open(self):
        #self.activate_pub.publish(self.activate_msg)
        goal=RobotiqSimpleCmd()
        goal.mech = 0 #right
        goal.close = False
        self.open_pub.publish(goal)
        self.open_pub.publish(goal)
        self.open_pub.publish(goal)
        print "Commanding Robotiq Open"
        rospy.sleep(3.0) 
