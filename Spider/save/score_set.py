import pymysql
import json
import csv
import time
import random
import pandas as pd
import numpy as np
from pandas import DataFrame
import os
from PIL import Image
from io import BytesIO

# 路径已经是绝对路径，不需要修改
filePath = 'C:\\Users\\admin\\Desktop\\T92488-高考志愿推荐\\Project\\Spider\\new_data\\高校分数线'

# 创建表函数
def create_score_table():
    try:
        db = pymysql.connect(host='localhost', user='root', password='123456', database='py_t92488')
        cursor = db.cursor()
        
        # 创建表
        create_sql = """
        CREATE TABLE IF NOT EXISTS Score_Table (
            ST_id INT AUTO_INCREMENT PRIMARY KEY,
            SI_id INT,
            Pro_id INT,
            ST_year VARCHAR(20),
            ST_batch VARCHAR(50),
            ST_type VARCHAR(50),
            ST_min INT,
            ST_average INT,
            ST_max INT,
            ST_people INT,
            INDEX(SI_id),
            INDEX(Pro_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        cursor.execute(create_sql)
        db.commit()
        print("分数表创建成功")
        cursor.close()
        db.close()
    except Exception as e:
        print("创建分数表失败:", str(e))

# 获取所有CSV文件函数
def get_all_csv_files(directory):
    all_files = []
    
    # 递归遍历所有子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                all_files.append(os.path.join(root, file))
    
    return all_files

# 插入数据函数
def insert_sql(i, data, col_name):
    try:
        # 打开数据库连接
        db = pymysql.connect(host='localhost', user='root', password='123456', database='py_t92488')
        cursor = db.cursor()
        sql = "INSERT IGNORE INTO Score_Table(" + col_name + ") VALUES(" + data + ")"
        cursor.execute(sql)
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        sql = "INSERT IGNORE INTO Score_Table(" + col_name + ") VALUES(" + data + ")"
        print(str(i), '插入失败：\n', sql)
        print("错误详情:", str(e))

# 处理CSV文件
def process_csv_file(csv_file):
    print(f"处理文件: {os.path.basename(csv_file)}")
    
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        
        # 如果存在Unnamed列，删除它
        if 'Unnamed: 0' in df.columns:
            del df['Unnamed: 0']
            
        # 检查CSV文件是否有数据
        if len(df) == 0:
            print(f"文件 {csv_file} 没有数据，跳过")
            return
            
        # 打印CSV列名，帮助调试
        print(f"CSV列名: {df.columns.tolist()}")
            
        # 构建列名映射
        col_name = []
        for i in df:
            col_name.append('ST_' + i)
            
        # 确保列索引在范围内
        if len(col_name) > 1:
            col_name[1] = 'SI_id'
        if len(col_name) > 2:
            col_name[2] = 'Pro_id'
            
        col_name = ','.join(col_name)
        print(f"数据库列名: {col_name}")
        
        # 打开一次数据库连接用于批量处理
        db = pymysql.connect(host='localhost', user='root', password='123456', database='py_t92488')
        cursor = db.cursor()
        
        # 记录成功和失败次数
        success_count = 0
        fail_count = 0
        
        # 处理每一行数据
        for i in range(len(df)):
            data = []
            for k in df:
                if pd.isna(df[k][i]):
                    data.append('"0"')  # 空值处理为0
                elif isinstance(df[k][i], str):
                    # 避免SQL注入，替换引号
                    clean_value = df[k][i].replace('"', '\\"').strip()
                    data.append(f'"{clean_value}"')
                else:
                    # 处理数值，去掉小数部分
                    try:
                        data.append(str(int(df[k][i])))
                    except:
                        data.append('"0"')  # 无法转换为整数时使用0
            
            # 连接数据
            data = ','.join(data)
            
            try:
                # 执行插入
                sql = "INSERT IGNORE INTO Score_Table(" + col_name + ") VALUES(" + data + ")"
                cursor.execute(sql)
                success_count += 1
                
                # 每100行提交一次
                if i % 100 == 0:
                    db.commit()
                    print(f"已处理 {i} 行")
            except Exception as e:
                print(f"行 {i} 插入失败: {str(e)}")
                print(f"SQL: {sql}")
                fail_count += 1
        
        # 最终提交
        db.commit()
        print(f"文件 {os.path.basename(csv_file)} 处理完成: {success_count} 成功, {fail_count} 失败")
        cursor.close()
        db.close()
        
    except Exception as e:
        print(f"处理文件 {csv_file} 时发生错误: {str(e)}")

# 主函数
def main():
    # 首先创建表
    create_score_table()
    
    # 获取所有CSV文件
    csv_files = get_all_csv_files(filePath)
    print(f"找到 {len(csv_files)} 个CSV文件")
    
    # 处理每个文件
    for csv_file in csv_files:
        process_csv_file(csv_file)
        print("-" * 50)

# 执行主函数
main()