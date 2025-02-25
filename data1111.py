import os
import re
import numpy as np
import matplotlib.pyplot as plt

def extract_timeslots(file_path):
    """Extracts the total timeslots for each scheduling algorithm from a given file."""
    timeslots = {"FIFO": [], "FIFO Merge": [], "RRRN": [], "RRRN Merge": []}

    print(f"Processing file: {file_path}")  # 调试输出
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        # 搜索匹配 "Total timeslots including failed requests" 的行
        for i, line in enumerate(lines):
            if "Total timeslots including failed requests" in line:
                rs_match = re.search(r"\((\d+)rs\)", line)
                if rs_match:
                    rs_value = int(rs_match.group(1))

                    # 读取接下来的四行，提取数据
                    for j in range(1, 5):
                        if i + j < len(lines):
                            entry = lines[i + j]
                            if "FIFO Merge" in entry:
                                timeslots["FIFO Merge"].append((rs_value, int(entry.split(":")[1].strip())))
                            elif "FIFO" in entry:
                                timeslots["FIFO"].append((rs_value, int(entry.split(":")[1].strip())))
                            elif "RRRN Merge" in entry:
                                timeslots["RRRN Merge"].append((rs_value, int(entry.split(":")[1].strip())))
                            elif "RRRN" in entry:
                                timeslots["RRRN"].append((rs_value, int(entry.split(":")[1].strip())))

    print(f"Extracted timeslots: {timeslots}")  # 调试输出
    return timeslots

def process_all_files(directory):
    """Processes all txt files in the specified directory to extract and average timeslots."""
    aggregated_timeslots = {"FIFO": {}, "FIFO Merge": {}, "RRRN": {}, "RRRN Merge": {}}

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            timeslots = extract_timeslots(file_path)

            for key in timeslots:
                for rs_value, slot_value in timeslots[key]:
                    if rs_value not in aggregated_timeslots[key]:
                        aggregated_timeslots[key][rs_value] = []
                    aggregated_timeslots[key][rs_value].append(slot_value)

    # Calculate the average
    avg_timeslots = {}
    for key in aggregated_timeslots:
        avg_timeslots[key] = {rs_value: np.mean(aggregated_timeslots[key][rs_value])
                              for rs_value in aggregated_timeslots[key]}

    print(f"Averaged timeslots: {avg_timeslots}")  # 调试输出
    return avg_timeslots

def plot_combined_avg_timeslots(avg_timeslots):
    """Plots a combined bar chart of the average total timeslots for each scheduling algorithm."""
    rs_values = sorted(list(avg_timeslots["FIFO"].keys()))

    bar_width = 0.2  # 设置每个柱子的宽度
    index = np.arange(len(rs_values))  # x轴的位置

    plt.figure(figsize=(10, 6))  # 调整图片大小和分辨率，宽度为3.5英寸，高度适当调整，保持高分辨率

    # 使用白底黑框柱状图，不同的填充图形来区分各个柱状图，并使用冷色调的颜色
    patterns = ["//", "\\", "--", "||"]
    colors = ['#ff7f0e', '#9467bd', '#2ca02c', '#17becf']

    plt.bar(index, [avg_timeslots['FIFO'][rs] for rs in rs_values], bar_width, label='FIFO', hatch=patterns[0], edgecolor='black', facecolor=colors[0])
    plt.bar(index + bar_width, [avg_timeslots['RRRN'][rs] for rs in rs_values], bar_width, label='Q-PBS without merge', hatch=patterns[1], edgecolor='black', facecolor=colors[1])
    plt.bar(index + 2 * bar_width, [avg_timeslots['FIFO Merge'][rs] for rs in rs_values], bar_width, label='FIFO Merge',
            hatch=patterns[2], edgecolor='black', facecolor=colors[2])
    plt.bar(index + 3 * bar_width, [avg_timeslots['RRRN Merge'][rs] for rs in rs_values], bar_width, label='Q-PBS',
            hatch=patterns[3], edgecolor='black', facecolor=colors[3])

    plt.xlabel('The Number of Concurrent Requests', fontsize=16)
    plt.ylabel('The Average Timeslots Consumption', fontsize=16)
    plt.title('The Average Timeslots Consumption for Different Scheduling Algorithms', fontsize=16)

    plt.xticks(index + 1.5 * bar_width, rs_values, fontsize=16)  # 调整x轴的刻度
    plt.yticks(fontsize=16)
    plt.legend(fontsize=16)

    plt.tight_layout()  # 调整图表布局以防止重叠
    plt.show()

if __name__ == "__main__":
    directory = "D:\\Code\\912"  # 指定txt文件所在的目录路径
    avg_timeslots = process_all_files(directory)
    plot_combined_avg_timeslots(avg_timeslots)
