import pyrealsense2 as rs
import numpy as np
import cv2
import time
import os

pipeline = rs.pipeline()

# Create a config并配置要流​​式传输的管道
config = rs.config()
config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)  # 深度图4:3
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)   # 彩图4:3

profile = pipeline.start(config)

depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()

align_to = rs.stream.color
align = rs.align(align_to)

# 按照日期创建文件夹
save_path = os.path.join(os.getcwd(), "IntelRealSense_L515", time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime()))

if not os.path.exists(save_path):    # 如果文件夹不存在则创建
    os.makedirs(save_path)
os.mkdir(os.path.join(save_path, "IntelRealSense_Color"))  # 创建彩图路径
os.mkdir(os.path.join(save_path, "IntelRealSense_Depth"))  # 创建深度路径

# 保存的图片和实时的图片界面
#cv2.namedWindow("live", cv2.WINDOW_AUTOSIZE)
cv2.namedWindow("s_SAVE,q_QUIT", cv2.WINDOW_AUTOSIZE) # S&Q
saved_color_image = None  # 保存的临时图片
saved_depth_mapped_image = None
saved_count = 0

# 主循环
try:
    while True:
        frames = pipeline.wait_for_frames()

        aligned_frames = align.process(frames)

        aligned_depth_frame = aligned_frames.get_depth_frame()  # 被对齐的深度图
        color_frame = aligned_frames.get_color_frame()

        if not aligned_depth_frame or not color_frame:
            continue

        depth_data = np.asanyarray(aligned_depth_frame.get_data(), dtype="float16")
        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())
        depth_mapped_image = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

        # 显示实时图像
        cv2.imshow("ColorLIVE", color_image)
        cv2.imshow("DepthLIVE", depth_mapped_image)

        # 打印分辨率和运行情况
        resolution_info = f"Color Resolution: {color_image.shape[1]}x{color_image.shape[0]}, Depth Resolution: {depth_image.shape[1]}x{depth_image.shape[0]}"
        print(resolution_info)

        key = cv2.waitKey(30)

        # s 保存图片
        if key & 0xFF == ord('s'):
            saved_color_image = color_image
            saved_depth_mapped_image = depth_mapped_image

            # 保存名称为时间加序号
            saved_name = f"{time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())}_{saved_count}"

            # 彩色图片保存为png格式
            cv2.imwrite(os.path.join(save_path, "IntelRealSense_Color", f"{saved_name}.png"), saved_color_image)
            cv2.imwrite(os.path.join(save_path, "IntelRealSense_Depth", f"{saved_name}.png"), saved_depth_mapped_image)

            # 深度信息由采集到的float16直接保存为npy格式
            np.save(os.path.join(save_path, "IntelRealSense_Depth", f"{saved_name}"), depth_data)
            saved_count += 1

            cv2.imshow("ColorSAVE", saved_color_image)  # 保存的彩色图像
            cv2.imshow("DepthSAVE", saved_depth_mapped_image)  # 保存的深度图像

        # q 退出
        if key & 0xFF == ord('q') or key == 27:
            cv2.destroyAllWindows()
            break
finally:
    pipeline.stop()
