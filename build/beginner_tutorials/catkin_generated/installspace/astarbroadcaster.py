#!/usr/bin/env python2
# -*- coding:UTF-8 -*-
import rospy
from nav_msgs.msg import Path,OccupancyGrid
from geometry_msgs.msg import PoseStamped,PoseWithCovarianceStamped
import time
import A_star
import numpy as np
import tf,tf.transformations
import math
th  = 0
# from scipy import interpolate
class PathBroadcaster():
        def __init__(self):
            rospy.init_node("path_pub")
            self.path_pub = rospy.Publisher("/path_my_A_star", Path, queue_size=15)
            self.path_pub_changed = rospy.Publisher("/path_my_A_star_changed", Path, queue_size=15)

            # 关于地图的一些变量
            self.origin_x = 0
            self.origin_y = 0
            self.resolution = 0
            self.width = 0
            self.height = 0
            # self.map_test_pub = rospy.Publisher("/map_test", OccupancyGrid, queue_size=15)
            self.map_sub = rospy.Subscriber("/amcl/map", OccupancyGrid, self.map_callback)
            
            self.current_path_changed = Path()
            rospy.sleep(1)
            # 起始点和目标点
            self.start_map_point = []
            self.goal_map_point = []
            # 地图上的路径
            self.path_map = []
            self.path_world = []
            # 是否要寻找路径的开关
            self.if_start_find_path = False
            self.goal_pose = PoseStamped()
            self.init_pose = PoseWithCovarianceStamped()
            self.init_pose_sub = rospy.Subscriber("/initialpose", PoseWithCovarianceStamped, self.init_pose_callback)
            self.goal_pose_sub = rospy.Subscriber("/move_base_simple/goal", PoseStamped, self.goal_pose_callback)
            self.last_time = rospy.get_rostime()
            self.start_find_path()
            rospy.Rate(1)
            
            rospy.spin()
        def init_pose_callback(self, msg):
            # print "===========get initial pose================"
            self.init_pose = msg
            # print msg
            # print "----------------worldtomap------------------"
            self.start_map_point =  self.WorldTomap(msg.pose.pose.position.x, msg.pose.pose.position.y)
            print( "----------------start point----------------",self.start_map_point)
            print( "value = "), self.map[self.start_map_point[0]][self.start_map_point[1]]
            if self.start_map_point == [-1, -1]:
                print( "\033[0;31m[E] : Please set the valid goal point\033[0m")
        def goal_pose_callback(self, msg):
            self.path_map = []
            self.goal_pose = msg
            self.if_start_find_path = True
            # print msg
            self.goal_map_point =  self.WorldTomap(msg.pose.position.x, msg.pose.position.y)
            print ("-----------------goal point---------------"),self.goal_map_point
            if self.goal_map_point == [-1, -1]:
                print ("\033[0;30m[Kamerider E] : Please set the valid goal point\033[0m")
                return
            else:
                self.start_find_path()
        def map_callback(self, msg):
            print (msg.header)
            print ("------")
            print (msg.info)
            print ("------")
            print (len(msg.data))
            # 初始化map里的参数值
            self.origin_x = msg.info.origin.position.x
            self.origin_y = msg.info.origin.position.y
            self.resolution = msg.info.resolution
            self.width = msg.info.width
            self.height = msg.info.height
            print ("-------",self.width)
            raw = np.array(msg.data, dtype=np.int8)
            self.map = raw.reshape((self.height, self.width))
            self.map_sub.unregister()
        def WorldTomap(self, wx, wy):
            # 返回-1，-1就是有问题
            # print wx, wy
            # print self.origin_x, self.origin_y
            if wx < self.origin_x or wy < self.origin_y:
                # print "<<<<<<<"
                return [-1, -1]
            mx = (int)((wx - self.origin_x) / self.resolution)
            my = (int)((wy - self.origin_y) / self.resolution)
            if mx < self.width and my < self.height:
                # print ">>>>>>>>>>>"
                return [my, mx]
            return [-1, -1] 
        def mapToWorld(self, my, mx):
            # 返回-1，-1就是有问题
            # print wx, wy
            # print self.origin_x, self.origin_y
            
            wx = mx*self.resolution+self.origin_x
            wy = my*self.resolution+self.origin_y
           
                # print ">>>>>>>>>>>"
            return [wx, wy]
                                              
        def start_find_path(self):
            if self.if_start_find_path:
                print ('\033[0;32m[I] : Start find path with A* \033[0m')
                temp = A_star.find_path(self.map, self.start_map_point, self.goal_map_point)
                self.path_map = temp.start_find()
                print (self.path_map)
                self.publisher_path()
            else:
                rospy.sleep(1)
                print ('\033[0;33m[W] : Please set goal pose\033[0m')
                return
        
        def publisher_path(self):
            time = 1
            y1 = []
            y2 = []
            current_path = Path()
            r = rospy.Rate(20)
            for i in range(len(self.path_map)):
                br = tf.TransformBroadcaster()
                br.sendTransform((0.0,0.0,0.0),(0.0,0.0,0.0,1.0),rospy.Time.now(),"odom","map")
                current_time = rospy.get_rostime()
                
                current_pose = PoseStamped()
                current_pose.header.stamp = current_time
                current_pose.header.frame_id = 'odom'
                current_pose.pose.position.x, current_pose.pose.position.y= self.mapToWorld(self.path_map[i][0], self.path_map[i][1])
                
                y1.append(self.mapToWorld(self.path_map[i][0], self.path_map[i][1])[0])
                y2.append(self.mapToWorld(self.path_map[i][0], self.path_map[i][1])[1])
                
                quat = tf.transformations.quaternion_from_euler(0,0,th)
                current_pose.pose.position.z = 0.0
                current_pose.pose.orientation.x = 0
                current_pose.pose.orientation.y = 0
                current_pose.pose.orientation.z = 0
                current_pose.pose.orientation.w = 1
                time += 1
                current_path.header.stamp = current_time
                current_path.header.frame_id = "odom"
                current_path.poses.append(current_pose) 
                if len(current_path.poses) > 1000:
                    current_path.poses.pop(0)
                self.path_pub.publish(current_path)
                r.sleep()
                self.last_time = current_time
                

            # # 通过差值做平滑处理
            # length = len(self.path_map)
            # x = np.array([num for num in range(length)])
            # xnew = np.arange(0,length - 1, 0.1)
            # func1 = interpolate.interp1d(x, y1, kind='cubic')
            # func2 = interpolate.interp1d(x, y2, kind='cubic')
            # ynew1 = func1(xnew)
            # ynew2 = func2(xnew)
            # for i in range(len(ynew1)):
            #     current_time = rospy.get_rostime()
            #     current_pose = PoseStamped()
            #     current_pose.pose.position.x = ynew1[i]
            #     current_pose.pose.position.y = ynew2[i]
            #     current_pose.pose.position.z = 0.0
            #     current_pose.pose.orientation.x = 0.0
            #     current_pose.pose.orientation.y = 0.0
            #     current_pose.pose.orientation.z = 0.0
            #     current_pose.pose.orientation.w = 1.0
            #     time += 1
            #     self.current_path_changed.header.stamp = current_time
            #     self.current_path_changed.header.frame_id = "odom"
            #     self.current_path_changed.poses.append(current_pose)
            #     self.path_pub_changed.publish(self.current_path_changed)
            #     self.last_time = current_time


br = PathBroadcaster()