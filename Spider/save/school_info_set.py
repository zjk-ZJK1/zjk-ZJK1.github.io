import pymysql
import json
import csv
import time
import random
import pandas as pd
import numpy as np
from pandas import DataFrame

# 修改为绝对路径
df = pd.read_csv("C:\\Users\\admin\\Desktop\\T92488-高考志愿推荐\\Project\\Spider\\new_data\\school_info3.csv")

# 检查CSV文件中的列
print("CSV文件中的列:")
for i, col in enumerate(df.columns):
    print(f"{i}: {col}")

# 根据Excel结构创建表
def create_excel_table():
    try:
        db = pymysql.connect(host='localhost', user='root', password='123456', database='py_t92488')
        cursor = db.cursor()
        
        # 删除表如果存在
        cursor.execute("DROP TABLE IF EXISTS School_Info")
        db.commit()
        
        # 创建与Excel结构匹配的表，将id改为自动递增
        create_sql = """
        CREATE TABLE School_Info (
            id INT AUTO_INCREMENT PRIMARY KEY,  /* 修改为自动递增 */
            school_id INT,
            name VARCHAR(255),
            code_enroll VARCHAR(50),
            belong VARCHAR(255),
            f985 VARCHAR(10),
            f211 VARCHAR(10),
            num_subject INT,
            num_master INT,
            num_doctor INT,
            num_academician INT,
            num_library INT,
            num_lab INT,
            province_id INT,
            is_recruitment VARCHAR(10),
            create_date VARCHAR(50),
            area VARCHAR(255),
            address VARCHAR(255),
            site VARCHAR(255),
            phone VARCHAR(100),
            email VARCHAR(100),
            introduction TEXT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        cursor.execute(create_sql)
        db.commit()
        print("表 School_Info 创建成功（ID字段设为自动递增）")
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print("创建表失败:", str(e))
        return False

# 创建表
create_excel_table()

# 插入数据
def insert_data():
    try:
        db = pymysql.connect(host='localhost', user='root', password='123456', database='py_t92488')
        cursor = db.cursor()
        
        # 清空表
        cursor.execute("TRUNCATE TABLE School_Info")
        
        # 获取表的所有列
        cursor.execute("SHOW COLUMNS FROM School_Info")
        columns = [col[0] for col in cursor.fetchall()]
        print("表中的列:", columns)
        
        # 逐行插入数据
        for i in range(len(df)):
            try:
                # 准备数据
                values = []
                placeholders = []
                column_names = []
                
                # 首先确保id字段存在且有值
                if 'id' in df.columns:
                    id_value = df['id'][i] if not pd.isna(df['id'][i]) else i+1
                else:
                    id_value = i+1  # 如果CSV中没有id列，使用行号+1作为id
                
                # 手动添加id字段
                column_names.append('id')
                placeholders.append("%s")
                values.append(int(id_value))
                
                # 遍历CSV的其他列
                for col in df.columns:
                    # 跳过已处理的id列
                    if col == 'id':
                        continue
                        
                    # 确认该列是否在表结构中
                    if col in columns:
                        column_names.append(col)
                        placeholders.append("%s")
                        
                        # 处理数据
                        if pd.isna(df[col][i]):
                            values.append(None)
                        else:
                            # 根据列名处理不同类型
                            if col in ['num_subject', 'num_master', 'num_doctor', 'num_academician', 
                                      'num_library', 'num_lab', 'province_id', 'school_id']:
                                try:
                                    values.append(int(df[col][i]))
                                except:
                                    values.append(0)
                            else:
                                values.append(str(df[col][i]))
                
                # 构建SQL
                if column_names:
                    sql = f"INSERT INTO School_Info ({', '.join(column_names)}) VALUES ({', '.join(placeholders)})"
                    cursor.execute(sql, values)
                
                # 每100行提交一次
                if i % 100 == 0:
                    print(f"已插入 {i} 条记录")
                    db.commit()
                    
            except Exception as e:
                print(f"插入第 {i} 行出错: {str(e)}")
                # 对于问题行，打印更多调试信息
                if i == 2888:
                    print("问题行数据:")
                    for col in df.columns:
                        print(f"{col}: {df[col][i]}")
        
        # 最终提交
        db.commit()
        print(f"共插入 {len(df)} 条记录")
        cursor.close()
        db.close()
        return True
    except Exception as e:
        print(f"数据插入失败: {str(e)}")
        return False

# 执行数据插入
insert_data()

