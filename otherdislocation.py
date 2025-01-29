import os
import glob
import csv
import re

# 12个等价方向(含正负) for c+a 家族: 1/6[2 -2 0 3]
CA_FAMILY = {
    # (A) 前12条常规枚举: w=+3 (6条) + w=-3 (6条)

    # w = +3
    (6,  2, -2,  0,  3),
    (6,  2,  0, -2,  3),
    (6,  0,  2, -2,  3),
    (6, -2,  2,  0,  3),
    (6, -2,  0,  2,  3),
    (6,  0, -2,  2,  3),

    # w = -3
    (6,  2, -2,  0, -3),
    (6,  2,  0, -2, -3),
    (6,  0,  2, -2, -3),
    (6, -2,  2,  0, -3),
    (6, -2,  0,  2, -3),
    (6,  0, -2,  2, -3),

    # (B) 后12条为对前12各自乘 -1 (等价但写法或顺序可能不同)

    (6, -2,  2,  0, -3),
    (6, -2,  0,  2, -3),
    (6,  0, -2,  2, -3),
    (6,  2, -2,  0, -3),
    (6,  2,  0, -2, -3),
    (6,  0,  2, -2, -3),
    (6, -2,  2,  0,  3),
    (6, -2,  0,  2,  3),
    (6,  0, -2,  2,  3),
    (6,  2, -2,  0,  3),
    (6,  2,  0, -2,  3),
    (6,  0,  2, -2,  3),
}

# 正则: 匹配"1/6[u v t w]"格式, 去除多余空格
REGEX_BURGERS = re.compile(r'''
    ^\s*
    1/(\d+)          # "1/6" -> group(1)=6
    \[
    \s*([-]?\d+)\s+([-]?\d+)\s+([-]?\d+)\s+([-]?\d+)
    \]
    \s*$
''', re.VERBOSE)

def parse_burgers(vec_str):
    """
    解析形如 "1/6[2 -2 0 3]" 字符串, 返回 (den, u, v, t, w).
    若格式错误, 返回 None.
    """
    m = REGEX_BURGERS.match(vec_str)
    if not m:
        return None
    den = int(m.group(1))
    u = int(m.group(2))
    v = int(m.group(3))
    t = int(m.group(4))
    w = int(m.group(5))
    return (den, u, v, t, w)

def is_in_ca_family(den, u, v, t, w):
    """判断(den,u,v,t,w) 是否在 c+a 家族 12个方向集合中"""
    return (den, u, v, t, w) in CA_FAMILY

def process_file(file_path):
    """
    对单个 CSV 文件:
      - 第二列(下标=1): 伯格斯矢量
      - 第四列(下标=3): 位错长度(浮点)
    若解析成功 & 属于 c+a 家族, 则累加计数 & 长度.
    """
    count = 0
    total_len = 0.0

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)  # 默认按逗号拆分
        for row in reader:
            if len(row) < 4:
                continue

            burg_str = row[1].strip()
            length_str = row[3].strip()

            parsed = parse_burgers(burg_str)
            if parsed is None:
                # 如果想调试: print("Failed parse:", repr(burg_str))
                continue

            (den, u, v, t, w) = parsed
            if is_in_ca_family(den, u, v, t, w):
                try:
                    length_val = float(length_str)
                except ValueError:
                    continue
                count += 1
                total_len += length_val

    return count, total_len

def main():
    # 1) 配置输入文件夹 & 输出汇总CSV
    input_folder = r"E:\08Mg\Paper\Proposal20240824\dforMg_CT\Mgtensdis"
    output_file  = r"E:\08Mg\Paper\Proposal20240824\dforMg_CT\Mgtensdis\summary.csv"

    # 2) 找到所有 *.csv
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))
    results = []

    # 3) 逐个处理
    for file_path in csv_files:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        c, total_len = process_file(file_path)
        results.append((base_name, c, total_len))

    # 4) 写出汇总
    with open(output_file, 'w', newline='', encoding='utf-8') as out_f:
        writer = csv.writer(out_f)
        writer.writerow(["Filename", "Count", "TotalLength"])
        for fname, cnt, length_sum in results:
            writer.writerow([fname, cnt, length_sum])

    print("Done! Summary ->", output_file)

if __name__ == "__main__":
    main()
