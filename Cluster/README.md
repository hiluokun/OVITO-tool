# `cluster2atom_cutoff.py`

## 🔍 简介

该脚本基于距离（cutoff）对指定类型的原子进行聚类分析，并将每一帧中参与聚类的原子集群用其质心（center of mass）替换，同时保留原始的 type 1 Na 原子。输出的新 LAMMPS dump 文件可用于后续分析或可视化。

---

## 📂 脚本路径

`cluster/cluster2atom_cutoff.py`

---

## 🛠 依赖环境

- Python 3.x
- [Ovito Python module](https://www.ovito.org/python/introduction/)
- `numpy`
- `tqdm`

可用以下命令安装：

```bash
pip install numpy tqdm
pip install --upgrade ovito

输入要求
LAMMPS trajectory dump 文件（含原子类型 type 1, 2,3，4）

非正交 cell 格式支持

每一帧包含完整的原子位置

cluster_cutoff = 2.4
cluster_types = {2, 4}
只对类型为 2 和 4 的原子聚类；

cutoff=2.4 表示距离小于 2.4 Å 的原子视为邻居。
 注意事项
若 unwrap_particles=True，需保证周期性边界条件设置正确；

若使用 only_selected=True，需确保 cluster_types 包含所有你希望纳入聚类的原子类型；

输出 COM 原子类型固定为 type 2（可改为其他）；

📚 相关链接
Ovito Python API - ClusterAnalysisModifier

Ovito 可视化软件
