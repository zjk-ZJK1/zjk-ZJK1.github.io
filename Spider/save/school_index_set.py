import pymysql
import json
import csv
import time
import random
import pandas as pd
import numpy as np
from pandas import DataFrame

df = pd.read_csv("C:\\Users\\admin\\Desktop\\T92488-高考志愿推荐\\Project\\Spider\\new_data\\school_index2.csv")
# print(df.info())
col_name = ['SI_id', 'SI_name', 'Img_1', 'Img_2', 'Img_3', 'Img_4', 'Img_5', 'Img_6', 'Img_name']
col_name = ','.join(col_name)

def insert_sql(i, data):
    try:
        # 打开数据库连接
        db = pymysql.connect(host='localhost', user='root', password='123456', database='py_t92488')
        # 使用 cursor() 方法创建一个游标对象 cursor
        cursor = db.cursor()
        # 使用 INSERT IGNORE 来避免主键冲突错误
        sql = "INSERT IGNORE INTO School_Index(" + col_name + ") values(" + data + ")"
        # print(sql)
        cursor.execute(sql)

        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        sql = "INSERT IGNORE INTO School_Index(" + col_name + ") values(" + data + ")"
        print(str(i), '插入失败：\n', sql)
        print("错误详情:", str(e))


# 优化循环处理，减少数据库连接次数
def batch_insert(df, batch_size=50):
    for start in range(0, len(df), batch_size):
        try:
            # 打开一次数据库连接
            db = pymysql.connect(host='localhost', user='root', password='123456', database='py_t92488')
            cursor = db.cursor()
            
            end = min(start + batch_size, len(df))
            print(f"处理记录 {start} 到 {end-1}")
            
            for i in range(start, end):
                data = []
                data.append(str(df['school_id'][i]))
                for k in df:
                    if k == 'school_id':
                        pass
                    else:
                        data.append("'" + str(df[k][i]) + "'")
                
                try:
                    data = ','.join(data)
                    # 使用 INSERT IGNORE 来避免主键冲突错误
                    sql = "INSERT IGNORE INTO School_Index(" + col_name + ") values(" + data + ")"
                    cursor.execute(sql)
                except Exception as e:
                    print(str(i), "处理失败:", str(e))
            
            db.commit()
            cursor.close()
            db.close()
            
        except Exception as e:
            print(f"批处理 {start}-{end-1} 失败:", str(e))


# 使用批处理替代单条插入
batch_insert(df)

# 注释掉原来的单条处理循环
'''
for i in range(len(df)):
    data = []
    data.append(str(df['school_id'][i]))
    for k in df:
        if k == 'school_id':
            pass
        else:
            data.append("'" + df[k][i] + "'")

    try:
        data = ','.join(data)
    except:
        print(str(i), "转化失败\n", data)

    insert_sql(i, data)
'''
