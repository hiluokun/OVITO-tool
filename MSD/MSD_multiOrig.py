#Minimum image convention
#This option tells OVITO whether or not to use the minimum image convention when calculating the displacement vectors for systems with periodic boundary conditions. You should deactivate this option if you work with unwrapped particle coordinates. In this case OVITO assumes that particle trajectories are all continuous. On the other hand, if you work with wrapped particle coordinates, this option should be turned on. The minimum image convention ensures that displacements are calculated correctly even when particles cross a periodic boundary of the cell and were mapped back into the cell by the simulation code. On the other hand, if you intend to calculate displacements vectors that span more than half of the simulation box size, then the minimum imagine convention cannot be used. You must use unwrapped coordinates in this case, because large displacements would otherwise be folded back into the periodic cell thanks to the minimum image convention.
#计算准确的MSD需要用到unwrap的坐标即 xu yu zu,而且需要关闭Minimum image convention。至于Affine mapping of the simulation cell（对应fix msd 里的com yes）其实影响没有这么大一般体积不会变化很大其实影响没有这么大一般体积不会变化很大ss）其实影响没有这么大一般体积不会变化很大

from ovito.io import import_file
from ovito.modifiers import CalculateDisplacementsModifier
from ovito.pipeline import ReferenceConfigurationModifier
import numpy as np
import time

# 记录开始时间
start_time = time.time()

# 加载输入数据并创建数据管道
#pipeline = import_file(r"D:\0work\09NaSPO\JMCAreply\Ox0npt1b473kNa.trj")

# 定义时间步长
delta_timestep = 10000.0  # 请根据实际情况修改

# 获取总帧数
total_frames = pipeline.source.num_frames
print("Total frames:", total_frames)

# 获取粒子数量
data0 = pipeline.compute(0)
num_particles = data0.particles.count
print("Number of particles:", num_particles)

# 定义 t0
t0_spacing = 1551  # t0 间隔为 200
t0_values = np.arange(0, total_frames, t0_spacing)
print("t0 values:", t0_values)

# 找到最大可能的 MSD 曲线长度
max_length = total_frames - 1

# 初始化一个二维数组，存储所有 t0 的 MSD 曲线，使用 np.nan 填充
msd_all = np.full((len(t0_values), max_length), np.nan)

# 遍历 t0_values
for idx_t0, t0 in enumerate(t0_values):
    # 清除之前的修改器
    pipeline.modifiers.clear()

    # 添加 CalculateDisplacementsModifier，设置参考帧为 t0
    calc_disp_mod = CalculateDisplacementsModifier()
    calc_disp_mod.affine_mapping = ReferenceConfigurationModifier.AffineMapping.ToCurrent
    calc_disp_mod.reference_frame = t0
    calc_disp_mod.minimum_image_convention = False  # 针对计算准确的MSD的 xu yu zu 需要关闭最小映像原则，
    pipeline.modifiers.append(calc_disp_mod)

    # 定义自定义修改器函数，用于计算位移平方
    def calculate_msd(frame, data):
        displacement_magnitudes = data.particles['Displacement Magnitude']
        squared_displacements = displacement_magnitudes ** 2
        # 将位移平方的平均值保存为全局属性
        data.attributes['MSD'] = np.mean(squared_displacements)

    # 添加自定义修改器到数据管道
    pipeline.modifiers.append(calculate_msd)

    # 计算从 t0 开始的 MSD 曲线
    max_dt = total_frames - t0 - 1

    msd_t0 = np.empty(max_dt)
    for dt in range(1, max_dt + 1):
        frame = t0 + dt
        data = pipeline.compute(frame)
        msd_value = data.attributes['MSD']
        msd_t0[dt - 1] = msd_value

    # 将 msd_t0 存储到 msd_all 数组的对应位置
    msd_all[idx_t0, :max_dt] = msd_t0

# 使用 numpy.nanmean() 计算平均 MSD 曲线
msd_average = np.nanmean(msd_all, axis=0)

# 生成 dTime 数组，对应于 msd_average 的有效数据长度
valid_length = np.count_nonzero(~np.isnan(msd_average))
dTime = np.arange(1, valid_length + 1) * delta_timestep

# 截取有效的 MSD 数据
msd_average = msd_average[:valid_length]

# 输出 MSD 数据到文件
output_file = r"D:\0work\09NaSPO\JMCAreply\Ox0npt1b473kNa_MSD1to.txt"
with open(output_file, 'w') as f:
    f.write("dTime MSD\n")
    for dt_value, msd_value in zip(dTime, msd_average):
        f.write(f"{dt_value} {msd_value}\n")

# 记录结束时间
end_time = time.time()
elapsed_time = end_time - start_time
hours = int(elapsed_time // 3600)
minutes = int((elapsed_time % 3600) // 60)
seconds = elapsed_time % 60
print(f"Total execution time: {hours}h {minutes}m {seconds:.2f}s")
