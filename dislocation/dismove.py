from ovito.io import import_file
import numpy as np

# 加载轨迹文件 统计每一帧中所有原子的最大和最小 X 位置，并减去一个参考原子的 X 坐标，以消除由于剪切变形引起的整体平移效应
pipeline = import_file(r"D:\0work\16ZnS\Indent\shear\ES\fix68ps\dump\fix68psHD.dump")

# 获取总帧数
total_frames = pipeline.source.num_frames
print("Total frames:", total_frames)

# 初始化一个集合，用于存储在所有帧中都存在的原子 ID
common_particle_ids = None

# 遍历所有帧，找到公共的原子 ID
for frame in range(total_frames):
    data = pipeline.compute(frame)
    particle_ids = set(data.particles['Particle Identifier'])

    if common_particle_ids is None:
        common_particle_ids = particle_ids
    else:
        common_particle_ids = common_particle_ids.intersection(particle_ids)

    # 打印进度（可选）
    print(f"Processed frame {frame}/{total_frames - 1}")

# 检查是否找到公共的原子 ID
if not common_particle_ids:
    print("No common particle IDs found in all frames.")
    exit()

# 选择第一个公共的原子 ID 作为参考原子
reference_particle_id = sorted(common_particle_ids)[0]
print("Reference particle ID:", reference_particle_id)

# 初始化数组，存储时间、调整后的最大 X、最小 X、参考原子 X 坐标
time_list = []
adjusted_max_x_list = []
adjusted_min_x_list = []
reference_x_list = []

# 定义时间步长（根据您的模拟参数修改）
delta_timestep = 1.0

# 遍历每一帧
for frame in range(total_frames):
    data = pipeline.compute(frame)

    # 获取所有原子的 X 坐标
    positions = data.particles['Position']
    x_positions = positions[:, 0]

    # 获取参考原子的索引（在数组中的位置）
    particle_ids = data.particles['Particle Identifier']
    reference_indices = np.where(particle_ids == reference_particle_id)[0]
    if len(reference_indices) == 0:
        print(f"Reference particle ID {reference_particle_id} not found in frame {frame}.")
        continue
    reference_index = reference_indices[0]

    # 获取参考原子的当前 X 坐标
    reference_x = positions[reference_index][0]

    # 记录参考原子的 X 坐标
    reference_x_list.append(reference_x)

    # 计算最大和最小 X 坐标
    max_x = np.max(x_positions)
    min_x = np.min(x_positions)

    # 计算调整后的最大和最小 X 坐标
    adjusted_max_x = max_x - reference_x
    adjusted_min_x = min_x - reference_x

    # 记录时间和结果
    current_time = frame * delta_timestep
    time_list.append(current_time)
    adjusted_max_x_list.append(adjusted_max_x)
    adjusted_min_x_list.append(adjusted_min_x)

    # 打印进度（可选）
    print(f"Frame {frame}/{total_frames - 1}: Time = {current_time}, Adjusted Max X = {adjusted_max_x}, Adjusted Min X = {adjusted_min_x}, Reference X = {reference_x}")

# 输出结果到文件
output_file = r"D:\0work\16ZnS\Indent\shear\ES\fix68ps\dump\fix68psHD.txt"
with open(output_file, 'w') as f:
    f.write("Time Adjusted_Max_X Adjusted_Min_X Reference_Particle_ID Reference_X\n")
    for t, max_x_adj, min_x_adj, ref_x in zip(time_list, adjusted_max_x_list, adjusted_min_x_list, reference_x_list):
        f.write(f"{t} {max_x_adj} {min_x_adj} {reference_particle_id} {ref_x}\n")

print("Calculation completed. Results saved to:", output_file)
