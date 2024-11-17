import pyrealsense2 as rs

# 创建管道
pipeline = rs.pipeline()
config = rs.config()

# 启用流
config.enable_stream(rs.stream.color)
config.enable_stream(rs.stream.depth)
config.enable_stream(rs.stream.infrared)

try:
    # 开始管道
    pipeline.start(config)
    print("Pipeline started successfully.")
except Exception as e:
    print(f"Error: {e}")
