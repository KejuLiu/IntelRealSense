import pyrealsense2 as rs

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1024, 768, rs.format.z16, 30) #可以修改分辨率
config.enable_stream(rs.stream.color, 1920, 1080, rs.format.rgb8, 30) #可以修改分辨率

cfg = pipeline.start(config)
device = cfg.get_device()
name = device.get_info(rs.camera_info.name)

print(name)

profile = cfg.get_stream(rs.stream.depth)
profile1 = cfg.get_stream(rs.stream.color)

inner_args = profile.as_video_stream_profile().get_intrinsics()
inner_args_2 = profile1.as_video_stream_profile().get_intrinsics()
inner_extrinsics = profile1.get_extrinsics_to(profile)

print(inner_extrinsics)
print("深度传感器内参：", inner_args)
print("RGB相机内参:", inner_args_2)
