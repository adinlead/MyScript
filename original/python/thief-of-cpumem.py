"""
本脚本的主要功能是模拟多进程环境下的 CPU 和内存占用，并通过蒙特卡罗方法估算圆周率。脚本会按照随机生成的参数循环运行，每次运行会模拟不同的 CPU 核数、内存占用和运算频率。

主要功能模块：
1. 配置管理：通过 config 字典管理运行参数，包括运行时长、运算频率、CPU 核数和内存占用等。
2. 时间格式化：time_str() 函数用于获取当前时间并格式化为包含周信息的字符串，方便日志输出。
3. 内存和 CPU 模拟：exec_func() 函数模拟内存占用，并在指定时间内进行圆周率估算。
4. 迭代次数测算：measure_iterations() 函数在迭代次数小于等于 1000 时，测算合适的迭代次数。
5. 内存分配：split_mem_randomly() 函数将总内存随机分配到多个 CPU 核上。
6. 主循环：main() 函数控制程序的主循环，按照随机参数创建并启动多个进程，模拟不同的运行环境。

使用方法：直接运行脚本，按 Ctrl+C 可终止程序。
"""
from calendar import c
import random
import time
import datetime
from multiprocessing import Process

# 配置参数，用于控制程序运行的各项随机参数
config = {
    # 1. 划分随机时间片段，每个片段时长在 min 和 max 秒之间
    'runtime':{
        'min':5,
        'max':60
    },
    # 2. 每个片段开始时，随机一个运算频率时间，取值在 min 和 max 之间（最多保留两位小数）
    'cpu_sleep_time':{
        'min':0.01,
        'max':0.7
    },
    # 3. 每个片段开始时，随机一个 CPU 核数，取值在 min 和 max 之间
    'cpu_count':{
        'min':1,
        'max':4
    },
    # 4. 每个片段开始时，随机一个内存占用数值，取值在 min 和 max 之间（单位：MB）
    'memory_used_mb':{
        'min':1000,
        'max':5000
    },
    # 迭代次数，大于 1000 时生效，用于控制圆周率估算的计算量
    'measure_iterations': 0
}

# 定义函数，用于获取当前时间并格式化为包含周信息的字符串
def time_str():
    # 获取当前日期和时间
    now = datetime.datetime.now()
    # 使用 isoweekday() 获取 ISO 标准的周信息（1 - 7，1 表示周一）
    isoweekday = now.isoweekday()
    # 格式化时间字符串，包含周信息和具体时间
    formatted_time_isoweek = f' 周{isoweekday} | ' + now.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_time_isoweek

# 定义执行函数，模拟 CPU 和内存占用操作，并估算圆周率
def exec_func(bt, ml, lt):
    try:
        # 模拟内存占用，创建一个指定大小的字符串
        cotext = ' ' * (ml * 1024 * 1024)
    except MemoryError:
        # 捕获内存不足异常并打印提示信息
        print("剩余内存不足，内存有溢出......")
    # 记录开始时间
    start_time = time.time()
    # 获取配置中的迭代次数
    measure_iterations = config['measure_iterations']
    # 在指定时间内持续进行圆周率估算
    while time.time() - start_time < lt:
        # 初始化圆内点的数量
        inside = 0
        # 进行指定次数的迭代
        for i in range(0, measure_iterations):
            # 生成随机点 (x, y)，范围在 [0, 1)
            x = random.random()
            y = random.random()
            # 判断点是否在单位圆内
            if x*x + y*y <= 1:
                inside += 1
        # 根据圆内点的数量估算圆周率
        pi_estimate = 4 * inside / 960000
        # 按照指定的运算频率时间进行休眠
        time.sleep(bt)

# 此处重复导入 random 模块，可移除
import random

# 定义函数，用于测算合适的迭代次数
def measure_iterations():
    # 当配置中的迭代次数小于等于 1000 时，进行迭代次数测算
    if config['measure_iterations'] <= 1000:
        print(f"【{time_str()}】正在测算迭代次数...")
        # 记录开始时间
        start_time = time.time()
        # 初始化迭代次数
        iterations = 0
        # 初始化已用时间
        elapsed = 0
        # 初始化圆内点的数量
        inside = 0
        # 持续运行 3 秒，测算迭代次数
        while elapsed < 3:
            # 生成随机点 (x, y)，范围在 [0, 1)
            x = random.random()
            y = random.random()
            # 判断点是否在单位圆内
            if x*x + y*y <= 1:
                inside += 1
            # 迭代次数加 1
            iterations += 1
            # 更新已用时间
            elapsed = time.time() - start_time
        # 根据 3 秒内的迭代次数计算 0.1 秒的迭代次数，并更新配置
        config['measure_iterations'] = int(iterations / 30)
        print(f"【{time_str()}】测算迭代次数完成，3秒内迭代次数:{iterations}，取值0.1秒次数:{config['measure_iterations']}")

# 定义函数，用于将一个整数值随机划分为指定数量的部分，确保各部分之和等于原数值
def split_mem_randomly(value, num):
    # 如果输入值或数量小于等于 0，返回空列表
    if value <= 0 or num <= 0:
        return []
    
    # 计算平均值
    avg = value // num
    # 计算平均值的一半
    half_avg = avg // 2
    
    # 初始化划分结果列表
    parts = []
    # 生成前 num - 1 个部分
    for _ in range(num - 1):
        # 在指定范围内随机生成整数
        part = int(random.uniform(max(1, avg - half_avg), min(value - sum(parts) - (num - len(parts) - 1), avg + half_avg)))
        parts.append(part)
    
    # 最后一份用剩余值确保总和等于输入值
    parts.append(value - sum(parts))
    return parts

# 定义主函数，程序的核心逻辑
def main():
    while True:
        # 1. 划分随机时间片段，获取本次运行的时长
        runtime = random.randint(config['runtime']['min'], config['runtime']['max'])
        # 2. 每个片段开始时，随机一个运算频率时间，取值在 0.01 - 0.7 之间（最多保留两位小数）
        cpu_sleep_time = round(random.uniform(config['cpu_sleep_time']['min'], config['cpu_sleep_time']['max']), 2)
        # 3. 每个片段开始时，随机一个 CPU 核数
        cpu_count = random.randint(config['cpu_count']['min'], config['cpu_count']['max'])
        # 4. 每个片段开始时，随机一个内存占用数值
        memory_used_mb = random.randint(config['memory_used_mb']['min'], config['memory_used_mb']['max'])
        # 打印当前运行参数信息
        print(f"【{time_str()}】运行时长:{runtime} 运算频率:{cpu_sleep_time} 占用cpu核数:{cpu_count} 占用内存:{memory_used_mb}MB")

        # 初始化进程列表
        ps_list = []
        # 尝试让进程列表中的进程结束，设置超时时间为 0.1 秒
        for p in ps_list:
            p.join(timeout=0.1)
        # 清空进程列表
        ps_list = []
        # 将内存占用数值随机划分为与 CPU 核数相同数量的部分
        mc = split_mem_randomly(memory_used_mb, cpu_count)
        # 为每个 CPU 核创建一个进程
        for i in range(0, cpu_count):
            ps_list.append(Process(target=exec_func, args=(cpu_sleep_time, mc[i], runtime)))
        # 启动所有进程
        for p in ps_list:
            p.start()

        # 记录开始时间
        start_time = time.time()
        # 在运行时长内每秒休眠一次
        while time.time() - start_time < runtime:
            time.sleep(1)
        # 运行结束后，随机休眠 0.5 - 3 秒
        time.sleep(round(random.uniform(0.5, 3), 2))

if __name__ == "__main__":
    # 调用测算迭代次数的函数
    measure_iterations()
    try:
        # 持续运行主函数
        while True:
            main()
    except KeyboardInterrupt:
        # 捕获用户按下 Ctrl+C 中断程序的信号，打印退出信息
        print("程序已经退出!")
