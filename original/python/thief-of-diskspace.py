"""
此脚本使用多线程的方式生成指定体积的随机二进制文件，文件扩展名为 tile。
可通过配置脚本中的 CONFIG 字典，灵活控制线程数、文件宽高范围等参数。

使用方法:
1. 自行修改WORKLOAD（脚本运行一次的工作量）、OUTPUT_DIR（输出目录）
2. 依据需要修改生成文件名，支持变量注入。
3. 在 CONFIG 字典中修改参数，可调整线程数、文件宽度和高度的取值范围。
4. 调用 write_data_to_files 函数，可自定义生成文件的总体积上限和输出目录。
5. 直接运行脚本，会按默认参数生成总计 10MB 的随机文件到当前工作目录。

生成文件名：
    1. 可在文件名中使用变量注入，如 %(level)d 表示文件层级，%(file_id)s 表示文件 ID，%(width)d 表示随机宽度，%(height)d 表示随机高度。
    2. 文件名中可使用 % 符号进行转义，如 %%(level)d 表示输出 % 符号和 level 变量。

思路：
    1. 计算每个线程需要生成的文件总体积，确保每个线程生成的文件总体积接近指定上限。
    2. 每个线程内根据文件层级生成随机数量的文件，层级越高数量越多。
    3. 每个线程内根据文件层级和数量，生成随机宽度和高度，并写入随机二进制数据。
        - 高度是指每个文件中，随机生成二进制数据的次数
        - 宽度是指内次随机生成的二进制数据长度
        - 即：每个文件中生成{高度}次{宽度}长的随机二进制数据
    4. 每个线程内根据文件层级和数量，生成随机文件名，并写入文件。

示例:
    # 生成 1GB 随机文件到 ./output 目录
    write_data_to_files(total_volume_limit=1024*1024*1024, output_dir='./output')
"""
import random
import os
import time
from uuid import uuid4
import threading

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB
GB = 1024 * MB

# 脚本运行一次的工作量
WORKLOAD = 1 * GB
# 输出目录
OUTPUT_DIR = "./"
# 支持变量注入：
# level 层级        file_id 文件ID
# width 宽度        height 高度
# timestamp 时间戳
FILE_NAME = "k%(level)d-%(file_id)s.tile"
# 脚本配置字典，包含以下参数：
CONFIG = {
    # thread_count: 线程数
    "thread_count":4,
    # width: 文件宽度范围
    "width":{
        "min":8000 * BYTE,
        "max":10000 * BYTE
    },
    # height: 文件高度范围
    "height":{
        "min":3000,
        "max":4000
    }
}

def generate_files_in_thread(output_dir, volume_per_thread):
    """
    在单个线程中生成随机文件，直到达到该线程分配的体积上限。

    :param output_dir: 输出文件的目录路径
    :param volume_per_thread: 当前线程需要生成的文件总体积上限，单位为字节
    """
    # 从配置中获取文件宽高的最小值和最大值
    width_min = CONFIG["width"]["min"]
    width_max = CONFIG["width"]["max"]
    height_min = CONFIG["height"]["min"]
    height_max = CONFIG["height"]["max"]
    # 记录当前线程已生成文件的总体积
    total_volume = 0
    # 遍历 0 到 4 级别的文件生成
    for level in range(0, 5):
        if level == 0:
            # 0 级文件生成 1 个
            count = 1
        else:
            # 非 0 级文件生成数量为当前级别数加上 0 到当前级别数的随机数
            count = level + random.randint(0, level)
        for _ in range(count):
            # 随机生成文件的宽度和高度
            width = random.randint(width_min, width_max)
            height = random.randint(height_min, height_max)
            # 计算当前文件的大小
            file_size = width * height
            # 如果生成当前文件会超过线程体积上限，则停止生成
            if total_volume + file_size > volume_per_thread:
                break
            # 生成唯一的文件 ID
            file_id = uuid4().hex
            timestamp = int(time.time() * 1000)
            # 拼接文件名
            filename = FILE_NAME % {
                "level":level, "file_id":file_id,
                "width":width, "height":height,
                "timestamp":timestamp,
            }
            # 拼接文件完整路径
            file_path = os.path.join(output_dir, filename)
            try:
                # 生成随机数据并写入文件，分 height 次写入，每次写入 width 个字节
                with open(file_path, 'wb') as f:
                    for _ in range(height):
                        chunk = bytes([random.randint(0, 255) for _ in range(width)])
                        f.write(chunk)
                # 更新已生成文件的总体积
                total_volume += file_size
            except IOError as e:
                print(f"写入文件 {file_path} 时出错: {e}")


def write_data_to_files(total_volume_limit=1024*1024*1024, output_dir='.'): 
    """
    多线程生成随机文件，确保生成文件的总体积不超过指定上限。

    :param total_volume_limit: 生成文件的总体积上限，单位为字节，默认为 1GB
    :param output_dir: 输出目录，默认为当前工作目录
    """
    # 确保输出目录存在
    thread_count = CONFIG["thread_count"]
    os.makedirs(output_dir, exist_ok=True)
    # 计算每个线程需要生成的文件体积
    volume_per_thread = total_volume_limit // thread_count
    # 存储所有线程对象
    threads = []
    for _ in range(thread_count):
        # 创建线程对象，指定目标函数和参数
        thread = threading.Thread(
            target=generate_files_in_thread,
            args=(output_dir, volume_per_thread)
        )
        threads.append(thread)
        # 启动线程
        thread.start()
    # 等待所有线程执行完毕
    for thread in threads:
        thread.join()

# 调用写入文件的方法
if __name__ == "__main__":
    write_data_to_files(total_volume_limit=WORKLOAD, output_dir=OUTPUT_DIR)
