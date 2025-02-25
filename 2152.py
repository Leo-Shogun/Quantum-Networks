import os
import re
import numpy as np
import matplotlib.pyplot as plt

def extract_delays(file_path):
    """
    从一个txt文件中提取 FIFO, FIFO Merge, RRRN Merge 三种算法
    在各个 (system_size, requests_number) 下的延迟信息。
    返回格式:
    {
      "FIFO": [(ss, rn, delay), ...],
      "FIFO Merge": [...],
      "RRRN Merge": [...]
    }
    """
    delays = {"FIFO": [], "FIFO Merge": [], "RRRN Merge": []}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        system_size = None
        requests_number = None

        for line in lines:
            # 提取 System size
            match = re.search(r"System size: (\d+)", line)
            if match:
                system_size = int(match.group(1))

            # 提取 requests number
            match = re.search(r"requests number: (\d+)", line)
            if match:
                requests_number = int(match.group(1))

            # FIFO
            match = re.search(r"Total FIFO delay: (\d+)", line)
            if match and system_size is not None and requests_number is not None:
                delays["FIFO"].append((system_size, requests_number, int(match.group(1))))

            # FIFO Merge
            match = re.search(r"Total FIFO Merge delay: (\d+)", line)
            if match and system_size is not None and requests_number is not None:
                delays["FIFO Merge"].append((system_size, requests_number, int(match.group(1))))

            # RRRN Merge
            match = re.search(r"Total RRRN after merge delay: (\d+)", line)
            if match and system_size is not None and requests_number is not None:
                delays["RRRN Merge"].append((system_size, requests_number, int(match.group(1))))

    return delays


def process_all_files(directory):
    """
    遍历目录下所有txt文件，汇总各算法在( system_size, requests_number )下的延迟，
    并取平均值。返回:
    avg_delays = {
        "FIFO": {
            (ss, rn): mean_delay,
            ...
        },
        "FIFO Merge": {
            ...
        },
        "RRRN Merge": {
            ...
        }
    }
    """
    aggregated = {"FIFO": {}, "FIFO Merge": {}, "RRRN Merge": {}}
    all_system_sizes = set()
    all_requests_numbers = set()

    for file_name in os.listdir(directory):
        if file_name.endswith('.txt'):
            file_path = os.path.join(directory, file_name)
            file_delays = extract_delays(file_path)

            for algo, records in file_delays.items():
                for (ss, rn, val) in records:
                    all_system_sizes.add(ss)
                    all_requests_numbers.add(rn)

                    if (ss, rn) not in aggregated[algo]:
                        aggregated[algo][(ss, rn)] = []
                    aggregated[algo][(ss, rn)].append(val)

    # 计算平均
    avg_delays = {}
    for algo in aggregated:
        avg_delays[algo] = {}
        for (ss, rn), val_list in aggregated[algo].items():
            avg_delays[algo][(ss, rn)] = np.mean(val_list)

    return avg_delays, sorted(all_system_sizes), sorted(all_requests_numbers)


def plot_ieee_singlecolumn_subplots(
    avg_delays,
    all_system_sizes,
    requests_numbers=[30, 60, 90],
    fig_title="Scheduling Results"
):
    """
    在同一个 Figure 中生成多个子图 (默认3行1列)，
    每个子图对应一个 requests_number。

    子图内容:
    - X轴: all_system_sizes
    - 柱状图(左Y轴): FIFO Merge & RRRN Merge的绝对延迟，不包含FIFO的柱子
    - 折线图(右Y轴): 它们相对于FIFO的延迟比值

    整个Figure宽度固定3.5英寸(IEEE单栏)，高度根据子图数量自动扩展。

    Parameters
    ----------
    avg_delays : dict
        形如 {
           "FIFO": {(ss, rn): mean_delay, ...},
           "FIFO Merge": {...},
           "RRRN Merge": {...}
        }
    all_system_sizes : list
        排序后的 system_size 列表
    requests_numbers : list
        需要绘制的请求数列表
    fig_title : str
        整个图的标题，可选
    """

    n_subplots = len(requests_numbers)
    # 让高度和子图数成比例，如每个子图2.5英寸，这里可根据需要微调
    fig_height = 2.5 * n_subplots

    # 创建Figure，宽=3.5英寸(IEEE单栏)，高=fig_height英寸
    fig, axes = plt.subplots(n_subplots, 1, figsize=(3.5, fig_height), sharex=False)
    fig.suptitle(fig_title, fontsize=10)  # 整个Figure的标题(可选)

    # 若只有1个子图时，axes不是list，需要强制转换
    if n_subplots == 1:
        axes = [axes]

    # 颜色、样式配置(可根据需求自定义)
    algo_colors = {
        "FIFO Merge": '#1f77b4',
        "RRRN Merge": '#ff7f0e'
    }
    line_styles = {
        "FIFO Merge": ('-', 'o'),   # 实线 + 圆点
        "RRRN Merge": ('--', '^')  # 虚线 + 三角
    }

    for idx, rn in enumerate(requests_numbers):
        ax1 = axes[idx]
        ax2 = ax1.twinx()  # 第二Y轴画变化率

        # 创建 X轴刻度
        x_indices = np.arange(len(all_system_sizes))

        # 准备两个算法的绝对延迟
        fifo_merge_abs = []
        rrrn_merge_abs = []

        # 计算对应的相对延迟(相对于 FIFO)
        fifo_merge_ratio = []
        rrrn_merge_ratio = []

        for ss in all_system_sizes:
            # 绝对延迟：FIFO Merge
            if (ss, rn) in avg_delays["FIFO Merge"]:
                val_fm = avg_delays["FIFO Merge"][(ss, rn)]
            else:
                val_fm = 0

            # 绝对延迟：RRRN Merge
            if (ss, rn) in avg_delays["RRRN Merge"]:
                val_rm = avg_delays["RRRN Merge"][(ss, rn)]
            else:
                val_rm = 0

            # FIFO
            if (ss, rn) in avg_delays["FIFO"]:
                val_fifo = avg_delays["FIFO"][(ss, rn)]
            else:
                val_fifo = 0

            fifo_merge_abs.append(val_fm)
            rrrn_merge_abs.append(val_rm)

            # 计算变化率
            if val_fifo != 0:
                fifo_merge_ratio.append(val_fm / val_fifo)
                rrrn_merge_ratio.append(val_rm / val_fifo)
            else:
                fifo_merge_ratio.append(np.nan)
                rrrn_merge_ratio.append(np.nan)

        # --- 画柱状图(只画 FIFO Merge & RRRN Merge) ---
        bar_width = 0.35  # 两个柱子并排
        ax1.bar(x_indices - bar_width/2, fifo_merge_abs,
                width=bar_width, color=algo_colors["FIFO Merge"], alpha=0.8, label="FIFO Merge")
        ax1.bar(x_indices + bar_width/2, rrrn_merge_abs,
                width=bar_width, color=algo_colors["RRRN Merge"], alpha=0.8, label="Q-PBS")

        # --- 画折线(相对FIFO) ---
        ls_fm, mk_fm = line_styles["FIFO Merge"]
        ls_rm, mk_rm = line_styles["RRRN Merge"]
        ax2.plot(x_indices, fifo_merge_ratio,
                 linestyle=ls_fm, marker=mk_fm, color=algo_colors["FIFO Merge"], label="FIFO Merge Ratio")
        ax2.plot(x_indices, rrrn_merge_ratio,
                 linestyle=ls_rm, marker=mk_rm, color=algo_colors["RRRN Merge"], label="Q-PBS Ratio")

        # 设置子图标题、坐标标签等
        ax1.set_title(f"Requests = {rn}", fontsize=9)
        ax1.set_ylabel("Abs. Delay", fontsize=8)
        ax2.set_ylabel("Relative to FIFO", fontsize=8)

        # 设置 X轴刻度和标签
        ax1.set_xticks(x_indices)
        ax1.set_xticklabels([str(s) for s in all_system_sizes], fontsize=8)

        # 如果只想让最下面的子图显示X轴标签，可在上面子图里 `ax1.set_xticklabels([])`
        # 这里暂不处理，保持每个子图都显示

        ax1.grid(axis='y', linestyle='--', alpha=0.7)

        # 合并图例
        h1, l1 = ax1.get_legend_handles_labels()
        h2, l2 = ax2.get_legend_handles_labels()
        # 去重或直接合并
        ax1.legend(h1 + h2, l1 + l2, fontsize=7, loc='best')

    # 调整子图布局，避免重叠
    plt.tight_layout()

    # 若 suptitle 与子图标题有重叠，可再手动调大 top
    # plt.subplots_adjust(top=0.90)

    plt.show()


def main():
    # 1) 指定放置 .txt 文件的目录
    directory = r"D:\Code\912"  # 修改为你的路径

    # 2) 解析文件，得到平均延迟数据
    avg_delays, all_system_sizes, all_requests_numbers = process_all_files(directory)
    print("All system_sizes:", all_system_sizes)
    print("All requests_numbers:", all_requests_numbers)

    # 3) 需要可视化的 requests_number，比如 [30, 60, 90]，只画三个子图
    selected_requests = [30, 60, 90]

    # 4) 画图: 3.5英寸宽，多个子图竖排
    plot_ieee_singlecolumn_subplots(
        avg_delays,
        all_system_sizes,
        requests_numbers=selected_requests,
        fig_title="Scheduling Results"
    )


if __name__ == "__main__":
    main()
