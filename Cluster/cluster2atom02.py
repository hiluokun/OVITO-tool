import numpy as np
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier, ClusterAnalysisModifier
from tqdm import tqdm

def extract_com_per_frame(input_dump, cutoff=2.4, cluster_types={2, 4}):
    pipeline = import_file(input_dump)

    # 选择哪些原子参与聚类
    pipeline.modifiers.append(
        SelectTypeModifier(property='Particle Type', types=cluster_types)
    )

    # 使用 Cutoff 模式的聚类分析，不再依赖 bond
    pipeline.modifiers.append(ClusterAnalysisModifier(
        cutoff=cluster_cutoff,
        compute_com=True,
        unwrap_particles=True,
        only_selected=True
            ))

    nframes = pipeline.source.num_frames
    all_coms = []

    for frame in tqdm(range(nframes), desc="Extracting COMs"):
        data = pipeline.compute(frame)
        com = data.tables['clusters']['Center of Mass']
        all_coms.append(com)

    return all_coms


def rewrite_dump_with_com(original_dump, output_dump, all_coms):
    with open(original_dump, 'r') as fin:
        lines = fin.readlines()

    output_lines = []
    i = 0
    frame_idx = -1

    while i < len(lines):
        line = lines[i]
        if line.startswith("ITEM: TIMESTEP"):
            frame_idx += 1
            coms = all_coms[frame_idx]

            # 写入 TIMESTEP 和其数值
            output_lines.append(lines[i])  # ITEM: TIMESTEP
            i += 1
            output_lines.append(lines[i])  # timestep value
            i += 1

            # 跳过原始原子数部分
            i += 1  # skip "ITEM: NUMBER OF ATOMS"
            i += 1  # skip original atom count line

            # 写入新原子数
            output_lines.append("ITEM: NUMBER OF ATOMS\n")
            atom_count_index = len(output_lines)
            output_lines.append("PLACEHOLDER\n")

            # 写入 BOX BOUNDS（header + 3 lines）
            for _ in range(4):
                output_lines.append(lines[i])
                i += 1

            # 写入 ATOM HEADER
            output_lines.append("ITEM: ATOMS id type x y z\n")
            i += 1  # skip original ATOMS header

            # 读取 type 1 原子
            frame_atoms = []
            max_atom_id = 0
            while i < len(lines) and not lines[i].startswith("ITEM: TIMESTEP"):
                line_clean = lines[i].strip()
                tokens = line_clean.split()
                if len(tokens) >= 2 and tokens[0].isdigit():
                    atom_id = int(tokens[0])
                    atom_type = int(tokens[1])
                    if atom_type == 1:
                        frame_atoms.append(lines[i])
                        if atom_id > max_atom_id:
                            max_atom_id = atom_id
                i += 1

            # 生成 COM 原子作为 type 2
            com_atoms = []
            for j, com in enumerate(coms):
                new_id = max_atom_id + 1 + j
                com_atoms.append(f"{new_id} 2 {com[0]:.10f} {com[1]:.10f} {com[2]:.10f}\n")

            # 更新原子数并写入
            total_atoms = len(frame_atoms) + len(com_atoms)
            output_lines[atom_count_index] = f"{total_atoms}\n"

            # 写入所有原子
            output_lines.extend(frame_atoms + com_atoms)

        else:
            i += 1

    with open(output_dump, 'w') as fout:
        fout.writelines(output_lines)


if __name__ == "__main__":
    input_dump = "final_trajectory.dump"
    output_dump = "output_with_com_cutoff02.dump"

    # 设置 cutoff 模式参数
    cluster_cutoff = 2.4
    cluster_types = {2, 4}

    # 步骤 1：提取每一帧 cluster COM
    all_coms = extract_com_per_frame(input_dump, cutoff=cluster_cutoff, cluster_types=cluster_types)

    # 步骤 2：重写 dump 文件
    rewrite_dump_with_com(input_dump, output_dump, all_coms)
