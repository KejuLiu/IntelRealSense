import cv2
import numpy as np
import pyrealsense2 as rs
import time
import os
import open3d as o3d

# 创建保存图像的目录
save_path = "captured_images"
if not os.path.exists(save_path):
    os.makedirs(save_path)

# 配置相机流
pipeline = rs.pipeline()
config = rs.config()

# 启用 RGB、深度和红外流
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30) # RGB
config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30)  # depth
config.enable_stream(rs.stream.infrared, 1, 1024, 768, rs.format.y8, 30)  # 红外

# 开始流
pipeline.start(config)

try:
    print("按下 'c' 键以捕获图像，按下 'q' 键退出。")
    while True:
        # 等待新帧
        frames = pipeline.wait_for_frames()

        # 获取各个流
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        infrared_frame = frames.get_infrared_frame()

        if not color_frame or not depth_frame or not infrared_frame:
            continue

        # 将帧转换为 NumPy 数组
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())
        infrared_image = np.asanyarray(infrared_frame.get_data())

        # 显示图像
        cv2.imshow('RGB Image', color_image)
        cv2.imshow('Depth Image', depth_image)
        cv2.imshow('Infrared Image', infrared_image)

        # 按下 'c' 键捕获图像
        key = cv2.waitKey(1)
        if key == ord('c'):
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            cv2.imwrite(os.path.join(save_path, f"rgb_{timestamp}.png"), color_image)
            cv2.imwrite(os.path.join(save_path, f"depth_{timestamp}.png"), depth_image)
            cv2.imwrite(os.path.join(save_path, f"infrared_{timestamp}.png"), infrared_image)
            print(f"Captured images at {timestamp}")

        # 按下 'q' 键退出
        elif key == ord('q'):
            break

finally:
    # 停止流
    pipeline.stop()
    cv2.destroyAllWindows()



