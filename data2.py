import matplotlib.pyplot as plt
def main():
    # 数据：将这些列表中的数值替换为你的实际数据
    requests = [50, 60, 70, 80, 90, 100]  # 请求数量
    timeslots_fidelity_07 = [30, 38, 45, 46, 47, 47]  # fidelity 0.7 的timeslots数量
    timeslots_fidelity_08 = [29, 33, 35, 39, 40, 40]  # fidelity 0.8 的timeslots数量
    timeslots_fidelity_09 = [21, 23, 28, 28, 29, 28]  # fidelity 0.9 的timeslots数量

    # 绘制曲线
    plt.figure(figsize=(10, 6))
    plt.plot(requests, timeslots_fidelity_07, marker='o', label='Fidelity 0.7')
    plt.plot(requests, timeslots_fidelity_08, marker='s', label='Fidelity 0.8')
    plt.plot(requests, timeslots_fidelity_09, marker='^', label='Fidelity 0.9')

    # 添加标题和标签
    plt.title('Timeslots vs. Requests for Different Fidelity Levels')
    plt.xlabel('Number of Requests')
    plt.ylabel('Number of Timeslots')
    plt.legend()
    plt.grid(True)

    # 显示图表
    plt.show()

if __name__ == "__main__":
    main()
