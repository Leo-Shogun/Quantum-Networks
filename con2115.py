import os
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def extract_timeslots(file_path):
    """Extracts the total timeslots for each scheduling algorithm from a given file."""
    timeslots = {"FIFO": [], "FIFO Merge": [], "RRRN": [], "RRRN Merge": []}

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
        avg_timeslots[key] = {}
        for rs_value in aggregated_timeslots[key]:
            avg_timeslots[key][rs_value] = np.mean(aggregated_timeslots[key][rs_value])
    return avg_timeslots

def plot_ieee_singlecolumn_bar_chart(avg_timeslots, fig_title="Timeslots Consumption"):
    """
    绘制单张柱状图:
      - X轴: 并发请求数量(rs_values)
      - Y轴: 平均timeslots
      - 4根柱子并排: FIFO, Q-PBS without merge (RRRN), FIFO Merge, Q-PBS (RRRN Merge)

    调整为适合 IEEE 单列 (3.5 英寸宽) 的排版。
    """
    rs_values = sorted(list(avg_timeslots["FIFO"].keys()))
    x_indices = np.arange(len(rs_values))

    # -----------------------------
    # 1) Figure: 3.5 英寸宽; 高度可根据内容微调
    # -----------------------------
    fig_width = 3.5
    fig_height = 2.8
    plt.figure(figsize=(fig_width, fig_height))

    # -----------------------------
    # 2) 绘制柱状图
    # -----------------------------
    bar_width = 0.18  # 每个柱子的宽度
    # 如果4种算法并排, 则总共占用 4*bar_width + 一点空隙

    # 为了区分, 设置一些 hatch 和 edgecolor
    patterns = ["//", "\\", "--", "||"]
    colors = ['#ff7f0e', '#9467bd', '#2ca02c', '#17becf']

    plt.bar(x_indices,
            [avg_timeslots['FIFO'][rs] for rs in rs_values],
            bar_width,
            label='FIFO',
            hatch=patterns[0],
            edgecolor='black',
            facecolor=colors[0])

    plt.bar(x_indices + bar_width,
            [avg_timeslots['RRRN'][rs] for rs in rs_values],
            bar_width,
            label='Q-PBS without merge',
            hatch=patterns[1],
            edgecolor='black',
            facecolor=colors[1])

    plt.bar(x_indices + 2 * bar_width,
            [avg_timeslots['FIFO Merge'][rs] for rs in rs_values],
            bar_width,
            label='FIFO Merge',
            hatch=patterns[2],
            edgecolor='black',
            facecolor=colors[2])

    plt.bar(x_indices + 3 * bar_width,
            [avg_timeslots['RRRN Merge'][rs] for rs in rs_values],
            bar_width,
            label='Q-PBS',
            hatch=patterns[3],
            edgecolor='black',
            facecolor=colors[3])

    # -----------------------------
    # 3) 坐标轴 & 标题 & 图例
    # -----------------------------
    # 小字号适应3.5英寸窄图
    font_label = 8
    font_tick = 7
    font_legend = 7
    font_title = 9

    plt.xlabel('Number of Concurrent Requests', fontsize=font_label)
    plt.ylabel('Average Timeslots Consumption', fontsize=font_label)
    plt.title(fig_title, fontsize=font_title)

    plt.xticks(x_indices + 1.5 * bar_width, rs_values, fontsize=font_tick)
    plt.yticks(fontsize=font_tick)
    plt.legend(fontsize=font_legend)

    # -----------------------------
    # 4) 布局调整, 避免重叠
    # -----------------------------
    plt.tight_layout()
    # 如果标题或图例与上方边界碰撞, 可再使用:
    # plt.subplots_adjust(top=0.88)

    # -----------------------------
    # 5) 显示或保存图
    # -----------------------------
    # plt.savefig("Timeslots_IEEE_Single.pdf", bbox_inches="tight")  # 若需导出PDF
    plt.show()

def main():
    directory = r"D:\Code\912"  # 指定txt文件所在的目录
    avg_timeslots = process_all_files(directory)

    # 绘制单栏柱状图
    plot_ieee_singlecolumn_bar_chart(avg_timeslots, fig_title="The Average Timeslots Consumption")

if __name__ == "__main__":
    main()
