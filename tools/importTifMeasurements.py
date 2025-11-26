import os
import glob
import re
from datetime import datetime
import psycopg2
from psycopg2 import extras
import rasterio
import config  # 导入数据库配置文件

# ================= 配置部分 =================
# 必须修改为你TIF文件的根目录，脚本会递归搜索所有 .tif 文件
TIF_BASE_PATH = r"../database/test/NO2/"

# 两个指定的站点坐标信息
TARGET_SITES = [
    {'site_id': 28, 'longitude': 116.404, 'latitude': 39.718},  # 大兴黄村
    {'site_id': 29, 'longitude': 116.47456, 'latitude': 39.78284},  # 大兴旧宫
]


# ================= 函数定义 =================
def generate_distinct_id(date_obj, hour, site_id, pollutant_id):
    """
    根据规则生成唯一的 distinct_id:
    "date-hour(两位整数)-site_id-pollute_id"
    例如: 2024-02-10-00281
    """
    date_str = date_obj.strftime('%Y-%m-%d')
    hour_str = str(hour).zfill(2)  # zfill(2) 实现了不足两位补0

    return f"{date_str}-{hour_str}{site_id}{pollutant_id}"


def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        # 默认自动提交是关闭的，这允许我们在 process_single_tif 中手动控制事务
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def load_pollutant_mapping(cursor):
    """获取污染物名称到ID的映射: { 'NO2': 1, ... }"""
    cursor.execute("SELECT pollutant_name, pollutant_id FROM pollutants")
    # 数据库中的名称可能为小写，但TIF路径中通常是大写，这里统一转为大写键
    return {name.upper(): id for name, id in cursor.fetchall()}


def parse_tif_path(file_path, pollutant_map):
    """
    解析TIF文件路径，提取污染物、日期和小时。
    Example path: .../NO2/2024_02_08/00.tif
    """
    # 使用正则表达式匹配路径中的关键信息：/污染物/日期/小时.tif
    # re.IGNORECASE 忽略大小写
    match = re.search(r'[/\\](\w+)[/\\](\d{4}_\d{2}_\d{2})[/\\](\d{2})\.tif$', file_path, re.IGNORECASE)

    if not match:
        return None

    pollutant_name, date_str, hour_str = match.groups()
    pollutant_name = pollutant_name.upper()

    try:
        pollutant_id = pollutant_map.get(pollutant_name)
        if pollutant_id is None:
            # 记录未知的污染物
            print(f"⚠️ 未知的污染物类型 '{pollutant_name}' 在路径: {file_path}")
            return None

        date_obj = datetime.strptime(date_str, '%Y_%m_%d').date()
        hour = int(hour_str)

        return {
            'pollutant_id': pollutant_id,
            'date': date_obj,
            'hour': hour,
            'data_dir': file_path
        }
    except Exception as e:
        print(f"⚠️ 日期或小时转换失败 ({file_path}): {e}")
        return None


def extract_pixel_value(tif_path, longitude, latitude):
    """
    使用 rasterio 读取TIF文件，提取指定经纬度点的像素值，并保留两位小数。
    """
    try:
        with rasterio.open(tif_path) as src:
            for value_array in src.sample([(longitude, latitude)]):
                value = value_array[0]

                # 检查 NoData 值（通常是 TIF 文件的背景值）
                if src.nodata is not None and value == src.nodata:
                    return None

                # 转换浮点数并保留两位小数
                return round(float(value), 2)

        return None
    except rasterio.RasterioIOError as e:
        # 打印文件读取错误，但允许程序继续处理下一个文件
        print(f"❌ 无法读取TIF文件 ({os.path.basename(tif_path)}): {e}")
        return None
    except Exception as e:
        # 捕捉其他可能的错误，如投影转换失败
        print(f"❌ 提取像素值时出错 ({os.path.basename(tif_path)}): {e}")
        return None


# ================= 核心修改函数：引入 conn 进行局部事务控制 =================
def process_single_tif(tif_path, conn, pollutant_map):
    """
    【关键修改】处理单个TIF文件，解析信息并提取目标站点数据，批量插入。
    - 引入 conn 参数，用于在函数内进行独立的 commit/rollback。
    - 使用 ON CONFLICT (distinct_id) DO NOTHING 实现主键冲突跳过。
    """
    # 标准化路径，以便在数据库中存储统一格式
    normalized_path = os.path.normpath(tif_path)
    parsed_info = parse_tif_path(normalized_path, pollutant_map)

    if not parsed_info:
        print(f"⚠️ 路径或污染物信息解析失败: {normalized_path}")
        return 0

    records_to_insert = []

    # 遍历目标站点，提取像素值
    for site in TARGET_SITES:
        site_id = site['site_id']
        longitude = site['longitude']
        latitude = site['latitude']

        # 提取值
        value = extract_pixel_value(normalized_path, longitude, latitude)

        if value is None:
            continue

        # 【新增健壮性检查】简单检查值是否为非负数
        if value < 0:
            print(f"⚠️ 像素值 ({value}) 无效（<0），已跳过。文件: {os.path.basename(tif_path)}, 站点: {site_id}")
            continue

        # 计算 distinct_id
        distinct_id = generate_distinct_id(
            parsed_info['date'],
            parsed_info['hour'],
            site_id,
            parsed_info['pollutant_id']
        )

        # 构造要插入的记录
        record = (
            distinct_id,
            site_id,
            parsed_info['pollutant_id'],
            parsed_info['date'],
            parsed_info['hour'],
            value,
            parsed_info['data_dir'],
        )
        records_to_insert.append(record)

    # 批量插入数据库
    if records_to_insert:
        cur = None
        try:
            cur = conn.cursor()

            # 【核心修改】使用 ON CONFLICT (distinct_id) DO NOTHING
            insert_query = """
                INSERT INTO measurements_tif (distinct_id, site_id, pollutant_id, date, hour, value, data_dir)
                VALUES %s
                -- 遇到 distinct_id 主键冲突时，直接跳过该条记录，不影响其他记录和事务。
                ON CONFLICT (distinct_id) DO NOTHING 
            """

            # 批量执行插入
            extras.execute_values(cur, insert_query, records_to_insert, template="(%s, %s, %s, %s, %s, %s, %s)")

            # 【关键修改】局部提交：提交当前 TIF 文件所做的全部插入，使其成为一个独立的事务。
            conn.commit()
            inserted_count = cur.rowcount  # 获取实际插入的行数（包含新增和更新）

            return inserted_count

        except Exception as e:
            # 【关键修改】如果发生非冲突错误（如类型错误），回滚当前事务，但只影响当前 TIF 文件。
            conn.rollback()
            print(f"❌ 数据库操作失败并回滚 (文件: {os.path.basename(tif_path)}): {e}")
            return 0
        finally:
            if cur:
                cur.close()

    return 0


# ================= 核心修改函数：main 函数 =================
def main():
    conn = get_db_connection()
    if not conn:
        return

    # 在 main 中只处理初始化和文件循环，数据操作的事务交给 process_single_tif
    pollutant_map = {}
    try:
        # 1. 加载污染物 ID 映射表
        with conn.cursor() as cur:
            pollutant_map = load_pollutant_mapping(cur)
        print(f"ℹ️ 加载了 {len(pollutant_map)} 个污染物类型。")

        # 2. 递归查找所有 TIF 文件
        tif_files = glob.glob(os.path.join(TIF_BASE_PATH, "**", "*.tif"), recursive=True)

        if not tif_files:
            print(f"❌ 在路径 '{TIF_BASE_PATH}' 及其子目录中未找到任何 TIF 文件。请检查 TIF_BASE_PATH 设置。")
            return

        print(f"✅ 找到 {len(tif_files)} 个 TIF 文件，开始处理...")

        total_inserted = 0

        # 使用 enumerate 可以显示进度
        for i, tif_file in enumerate(tif_files):
            # 将 conn 传递给 process_single_tif，让它在内部管理事务
            inserted_count = process_single_tif(tif_file, conn, pollutant_map)
            total_inserted += inserted_count
            # 打印进度和结果
            print(f"[{i + 1}/{len(tif_files)}] -> {os.path.basename(tif_file)}: 成功插入 {inserted_count} 条记录。")

        # 【移除】不再需要 conn.commit()，每个 TIF 文件已独立提交
        print(f"🎉 所有 TIF 文件处理完毕，共插入 {total_inserted} 条记录。")

    except Exception as e:
        # 捕捉初始化阶段（如加载污染物映射表）的错误
        print(f"❌ 发生严重错误（初始化或文件查找），程序中止: {e}")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()