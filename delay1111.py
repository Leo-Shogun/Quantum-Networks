import os
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib  # Import matplotlib to access colormaps


def extract_delays(file_path):
    """Extracts the total delays for each scheduling algorithm from a given file."""
    delays = {"FIFO": [], "FIFO Merge": [], "RRRN Merge": []}

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

        system_size = None
        requests_number = None

        for line in lines:
            # Extract System size
            match = re.search(r"System size: (\d+)", line)
            if match:
                system_size = int(match.group(1))

            # Extract requests number
            match = re.search(r"requests number: (\d+)", line)
            if match:
                requests_number = int(match.group(1))

            # Extract FIFO delay
            match = re.search(r"Total FIFO delay: (\d+)", line)
            if match and system_size is not None and requests_number is not None:
                fifo_delay = int(match.group(1))
                delays["FIFO"].append((system_size, requests_number, fifo_delay))

            # Extract FIFO Merge delay
            match = re.search(r"Total FIFO Merge delay: (\d+)", line)
            if match and system_size is not None and requests_number is not None:
                fifo_merge_delay = int(match.group(1))
                delays["FIFO Merge"].append((system_size, requests_number, fifo_merge_delay))

            # Extract RRRN Merge delay
            match = re.search(r"Total RRRN after merge delay: (\d+)", line)
            if match and system_size is not None and requests_number is not None:
                rrrn_merge_delay = int(match.group(1))
                delays["RRRN Merge"].append((system_size, requests_number, rrrn_merge_delay))

    return delays


def process_all_files(directory):
    """Processes all txt files in the specified directory to extract and average delays."""
    aggregated_delays = {"FIFO": {}, "FIFO Merge": {}, "RRRN Merge": {}}
    all_system_sizes = set()
    all_requests_numbers = set()

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            file_path = os.path.join(directory, filename)
            delays = extract_delays(file_path)

            for key in delays:
                for system_size, requests_number, delay_value in delays[key]:
                    all_system_sizes.add(system_size)
                    all_requests_numbers.add(requests_number)

                    if (system_size, requests_number) not in aggregated_delays[key]:
                        aggregated_delays[key][(system_size, requests_number)] = []
                    aggregated_delays[key][(system_size, requests_number)].append(delay_value)

    # Calculate the average
    avg_delays = {}
    for key in aggregated_delays:
        avg_delays[key] = {
            (system_size, requests_number): np.mean(aggregated_delays[key][(system_size, requests_number)])
            for (system_size, requests_number) in aggregated_delays[key]
        }

    return avg_delays, sorted(all_system_sizes), sorted(all_requests_numbers)


def plot_combined_relative_delays_by_system_size(avg_delays, all_system_sizes, all_requests_numbers, base_algo='FIFO'):
    """
    Plots relative delays for FIFO Merge and RRRN Merge compared to base_algo, varying system size,
    with multiple lines for different requests numbers.
    """
    plt.figure(figsize=(10, 6))  # Set figure size to IEEE single-column width (3.5 inches width)
    data_plotted = False  # Flag to check if any data was plotted

    # Generate a list of colors using a distinct colormap
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Distinct colors for better differentiation

    selected_requests_numbers = [30, 60, 90]

    # Set X-axis ticks for grid alignment
    xticks = sorted(all_system_sizes)
    plt.xticks(xticks)  # Explicitly set X-axis ticks

    for compare_algo, marker_style in zip(['FIFO Merge', 'RRRN Merge'], ['^', 'o']):  # FIFO Merge with square, RRRN Merge with circle
        for idx, rn in enumerate(selected_requests_numbers):
            system_sizes = sorted(set([k[0] for k in avg_delays[base_algo].keys() if k[1] == rn]))
            relative_delays = []
            ss_values = []
            for ss in system_sizes:
                if (ss, rn) in avg_delays[compare_algo] and (ss, rn) in avg_delays[base_algo]:
                    base_delay = avg_delays[base_algo][(ss, rn)]
                    if base_delay != 0:
                        relative_delay = avg_delays[compare_algo][(ss, rn)] / base_delay
                        relative_delays.append(relative_delay)
                        ss_values.append(ss)
            if relative_delays:
                print(f'Plotting {compare_algo} for Requests Number = {rn}, Data Points = {len(relative_delays)}')
                plt.plot(ss_values, relative_delays, marker=marker_style, linestyle='-',  # Solid line for both
                         label=f'{compare_algo} - Requests Number = {rn}', color=colors[idx % len(colors)])
                data_plotted = True
            else:
                print(f'No data to plot for {compare_algo} and Requests Number = {rn}')
    plt.xlabel('System Size', fontsize=16)  # 设置 X 轴标签字体大小
    plt.ylabel('Relative Delay', fontsize=16)  # 设置 Y 轴标签字体大小
    plt.title(f'Relative Delay of FIFO Merge and Q-PBS', fontsize=16)  # 设置标题字体大小
    plt.tick_params(axis='both', which='major', labelsize=16)  # 设置刻度标签的字体大小

    if data_plotted:
        plt.legend(fontsize=16)  # 设置图例字体大小，保持较小以适应单列图
    else:
        print('No data was plotted. Skipping legend.')

    plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)  # Set grid appearance
    plt.ylim(0.2, 0.7)  # 设置统一的 Y 轴范围
    plt.yticks(np.arange(0.2, 0.75, 0.1))  # 设置 Y 轴的刻度值
    plt.tight_layout()  # 调整布局以适应单列宽度
    plt.show()


if __name__ == "__main__":
    directory = "D:\\Code\\912"  # Specify the directory containing txt files
    avg_delays, all_system_sizes, all_requests_numbers = process_all_files(directory)

    # Plotting combined relative delays by system size for FIFO Merge and RRRN Merge
    plot_combined_relative_delays_by_system_size(
        avg_delays,
        all_system_sizes,
        all_requests_numbers,
        base_algo='FIFO'
    )
