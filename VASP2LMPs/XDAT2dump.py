from ovito.io import import_file, export_file
import os

# 路径定义
xdatcar_path = 'XDATCAR'  # 你的XDATCAR路径
data_frames_dir = 'data_frames'  # 中间data文件夹
final_dump_file = 'final_trajectory.dump'  # 最终输出dump文件名

# 创建文件夹保存中间data文件
if not os.path.exists(data_frames_dir):
    os.makedirs(data_frames_dir)

# 步骤1: 读取XDATCAR并逐帧输出为LAMMPS data文件
pipeline = import_file(xdatcar_path)
num_frames = pipeline.source.num_frames

for frame in range(num_frames):
    export_file(pipeline, 
                os.path.join(data_frames_dir, f'frame_{frame}.data'), 
                'lammps/data', 
                frame=frame)
    print(f'Frame {frame} exported as data file.')

# 步骤2: 从导出的data文件重新导入为轨迹
data_files_pattern = os.path.join(data_frames_dir, 'frame_*.data')
new_pipeline = import_file(data_files_pattern, multiple_frames=True)

# 步骤3: 导出轨迹为LAMMPS dump文件，显式指定columns
export_file(new_pipeline, 
            final_dump_file, 
            'lammps/dump', 
            multiple_frames=True,
            columns=[
                'Particle Identifier', 
                'Particle Type', 
                'Position.X', 
                'Position.Y', 
                'Position.Z'
            ])

print(f'Final dump trajectory saved to {final_dump_file}')
