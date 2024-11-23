import cv2
import sys
import pyrealsense2 as rs
import numpy as np
import time
import png
import os


def writeVideo(videoPath, depthSubDir, rgbSubDir):
     #开启视频输入
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 保存视频的编码

    #将rgb相机与深度图对齐
    align_to = rs.stream.color
    align = rs.align(align_to)

    #深度图帧图像滤波器
    hole_filling_filter=rs.hole_filling_filter(2)

    #配置文件
    pipe = rs.pipeline()
    cfg = rs.config()
    profile = pipe.start(cfg)
    # D400相机开启参数
    cfg.enable_stream(rs.stream.depth,640,480,rs.format.z16,30)
    cfg.enable_stream(rs.stream.color,640,480,rs.format.bgr8,30)
    out = cv2.VideoWriter(videoPath, fourcc, 30, (640, 480))  # 帧数为30


    # L515相机开启参数
    # Declare sensor object and set options
    # cfg.enable_stream(rs.stream.depth,640,480,rs.format.z16,30)
    # cfg.enable_stream(rs.stream.color,1280,720,rs.format.bgr8,30)
    # out = cv2.VideoWriter(videoPath, fourcc, 30, (1280, 720))  # 帧数为30
    # depth_sensor = profile.get_device().first_depth_sensor()
    # depth_sensor.set_option(rs.option.visual_preset, 5)  # 5 is short range, 3 is low ambient light
    # depth_sensor.set_option(rs.option.laser_power, 80)
    # depth_sensor.set_option(rs.option.min_distance, 0)


    #当前的图片id
    now_id=0

    try:
        while True:
            #获取帧图像
            frame = pipe.wait_for_frames()

            #对齐之后的frame
            aligned_frame = align.process(frame)

            #获得数据帧
            depth_frame = aligned_frame.get_depth_frame()
            color_frame = aligned_frame.get_color_frame()

            # 深度参数，像素坐标系转相机坐标系用到，要拿彩色作为内参，因为深度图会对齐到彩色相机
            color_intrin = color_frame.profile.as_video_stream_profile().intrinsics
            # print('color_intrin:', color_intrin)

            #将深度图彩色化的工具
            colorizer = rs.colorizer()

            #将彩色图和深度图进行numpy化
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)

            #输入视频
            out.write(color_image)
            #将深度图彩色化
            colorized_depth = np.asanyarray(colorizer.colorize(depth_frame).get_data())
            all_images = np.hstack((color_image, colorized_depth))

            # 图像展示
            cv2.imshow('all_images', all_images)

            #帧数设定
            key = cv2.waitKey(30)

            now_id+=1



            #按键事件
            if key == ord("q"):
                print('用户退出！')
                break
            elif key == ord("s"):  #保存深度图和彩色图
                with open(depthSubDir+ '/' +str(now_id)+".png", 'wb') as f:
                    writer = png.Writer(width=depth_image.shape[1], height=depth_image.shape[0],
                                        bitdepth=16, greyscale=True)
                    zgray2list = depth_image.tolist()
                    writer.write(f, zgray2list)
                # with open('./grape1_rgbImgs/' + '/' + str(now_id) + ".png") as f:
                    # writer = png.Writer(width=color_image.shape[1], height=color_image.shape[0],
                    #                     bitdepth=16, greyscale=True)
                    # zgray2list = color_image.tolist()
                    # cv2.imwrite(f, color_image)
                rgb_file = rgbSubDir + '/' + str(now_id) + ".png"
                depth_file = depthSubDir+ '/' +str(now_id)+".png"
                cv2.imwrite(rgbSubDir + '/' + str(now_id) + ".png", color_image)
                print("保存文件 {} and {}成功！".format(rgb_file, depth_file))
                continue


    finally:
        pipe.stop()
        out.release()


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


if __name__ == "__main__":
    #获取时间标记
    t = time.localtime()
    this_time = str(str(t.tm_hour) + "_" + str(t.tm_min) + "_" + str(t.tm_sec)) # 路径不接受中文
    videoPath = f"./grape1_videos/{this_time}.avi"
    depthSubDir = os.path.join('grape1_depthImgs', this_time)
    rgbSubDir = os.path.join('grape1_rgbImgs', this_time)
    mkdir(depthSubDir)
    mkdir(rgbSubDir)
    writeVideo(videoPath, depthSubDir, rgbSubDir)