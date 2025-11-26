import os
import glob
import pandas as pd
import psycopg2
from psycopg2 import extras
# 确保 config.py 能够被导入
import config
from datetime import datetime  # 导入 datetime 库用于日期处理

# ================= 配置部分 =================
# 指定存放 CSV 文件的文件夹路径 (默认当前目录)
CSV_FOLDER_PATH = r'../database/test/' #这里是csv数据的目录


# ===========================================

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
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def load_id_mappings(cursor):
    """
    为了提高性能，先将数据库中的 site_name 和 pollutant_name
    映射为对应的 ID，存入字典中，避免每插入一行都去查询 ID。
    """
    # 获取站点映射: { '东城东四': 1, ... }
    cursor.execute("SELECT site_name, site_id FROM sites")
    site_map = dict(cursor.fetchall())

    # 获取污染物映射: { 'NO2': 1, ... }
    cursor.execute("SELECT pollutant_name, pollutant_id FROM pollutants")
    pollutant_map = dict(cursor.fetchall())

    return site_map, pollutant_map


def generate_distinct_id(date_str, hour, site_id, pollutant_id):
    """
    根据规则生成唯一的 distinct_id:
    "date-hour(两位整数)-site_id-pollute_id"
    例如: 2024-02-10-00281
    """
    # hour_val 是整数，zfill(2) 实现了不足两位补0
    hour_str = str(hour).zfill(2)

    # 格式化并组合
    return f"{date_str}-{hour_str}{site_id}{pollutant_id}"


def process_csv_and_insert(file_path, cursor, site_map, pollutant_map):
    print(f"📄 正在处理文件: {file_path} ...")

    try:
        # 1. 读取 CSV
        df = pd.read_csv(file_path)

        # 2. 数据转换 (Wide to Long)
        id_vars = ['data', 'hour', 'type']
        value_vars = [col for col in df.columns if col not in id_vars]

        melted_df = df.melt(
            id_vars=id_vars,
            value_vars=value_vars,
            var_name='site_name',
            value_name='value'
        )

        # 3. 数据清洗
        melted_df = melted_df.dropna(subset=['value'])

        # 准备批量插入的数据列表
        records_to_insert = []

        for _, row in melted_df.iterrows():
            date_val = row['data']  # CSV header 是 data (例如: '2024-01-01')
            hour_val = row['hour']
            pollutant_name = row['type']
            site_name = row['site_name']
            value = row['value']

            # 获取 ID
            site_id = site_map.get(site_name)
            pollutant_id = pollutant_map.get(pollutant_name)

            # 检查站点或污染物是否存在于数据库中
            if site_id is None:
                continue
            if pollutant_id is None:
                print(f"⚠️ 警告: 污染物 '{pollutant_name}' 在数据库 pollutants 表中不存在，跳过。")
                continue

            # 【新增】生成 distinct_id
            distinct_id = generate_distinct_id(date_val, hour_val, site_id, pollutant_id)

            # 【修改】将 distinct_id 添加到记录中
            records_to_insert.append((distinct_id, site_id, pollutant_id, date_val, hour_val, value))

        # 4. 批量插入数据库
        if records_to_insert:
            insert_query = """
                -- 【修改】包含 distinct_id 字段
                INSERT INTO measurements (distinct_id, site_id, pollutant_id, date, hour, value)
                VALUES %s
                -- 由于 distinct_id 是主键，如果重复则会冲突，但这里使用 DO NOTHING 保持幂等性
                ON CONFLICT DO NOTHING
            """
            # 【修改】execute_values 模板需要 6 个参数 (distinct_id, site_id, pollutant_id, date, hour, value)
            extras.execute_values(cursor, insert_query, records_to_insert, template="(%s, %s, %s, %s, %s, %s)")
            return len(records_to_insert)
        else:
            print("⚠️ 该文件没有有效数据可插入。")
            return 0

    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {e}")
        # 抛出异常，以便 main 函数可以捕获并进行回滚
        raise e


def main():
    conn = get_db_connection()
    if not conn:
        return

    try:
        cur = conn.cursor()

        # 加载 ID 映射表
        site_map, pollutant_map = load_id_mappings(cur)
        print(f"ℹ️ 加载了 {len(site_map)} 个站点和 {len(pollutant_map)} 个污染物类型。")

        # 查找所有 CSV 文件
        csv_files = glob.glob(os.path.join(CSV_FOLDER_PATH, "*.csv"))

        if not csv_files:
            print(f"❌ 在路径 '{CSV_FOLDER_PATH}' 中未找到任何 CSV 文件。")
            return

        total_inserted = 0

        for csv_file in csv_files:
            inserted_count = 0
            file_name = os.path.basename(csv_file)
            print(f"🔍 正在处理文件: {file_name}")

            try:
                # 尝试处理文件
                inserted_count = process_csv_and_insert(csv_file, cur, site_map, pollutant_map)
                total_inserted += inserted_count

                # 【增强事务】单个文件处理成功后立即提交
                conn.commit()
                print(f"✅ 文件 {file_name} 处理成功，插入 {inserted_count} 条记录并已提交。")

            except Exception as file_error:
                # 【增强事务】如果单个文件处理失败，回滚当前文件的操作
                conn.rollback()
                print(f"❌ 文件 {file_name} 处理失败，操作已回滚。")
                print(f"❌ 详细错误: {type(file_error).__name__}: {file_error}")
                # 继续处理下一个文件

        print(f"🎉 所有文件处理完毕，数据库操作结束。总计插入 {total_inserted} 条记录。")

    except Exception as e:
        # 捕获连接或初始设置的错误
        if conn and 'cur' in locals():
            conn.rollback()
        print(f"❌ 发生主程序错误或连接错误，已回滚所有未提交操作。")
        print(f"❌ 详细错误: {type(e).__name__}: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()