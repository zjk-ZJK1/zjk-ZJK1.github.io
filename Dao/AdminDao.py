import pymysql
import json
from Dao.UserDao import get_connection

def get_scores_list(page, size, school_name='', province_id='', year=''):
    """获取分数线数据列表"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    # 检查表结构
    try:
        cursor.execute("DESCRIBE score_table")
        columns = cursor.fetchall()
        column_names = [col['Field'] for col in columns]
        
        # 构建SELECT字段列表和WHERE条件
        select_fields = ['s.ST_id', 's.SI_id', 's.ST_School_name']
        
        # 添加省份相关字段（如果存在）
        province_column = None
        for col in column_names:
            if 'province' in col.lower():
                province_column = col
                select_fields.append(f's.{col}')
                break
        
        # 添加其他常用字段
        for field in ['ST_Min', 'ST_Average', 'ST_Max', 'ST_Year', 'ST_Type', 'ST_Local_batch_name']:
            if field in column_names:
                select_fields.append(f's.{field}')
        
        # 设置查询参数
        offset = (page - 1) * size
        params = []
        where_clause = []
        
        if school_name:
            where_clause.append("s.ST_School_name LIKE %s")
            params.append(f"%{school_name}%")
        
        if province_id and province_column:
            where_clause.append(f"s.{province_column} = %s")
            params.append(province_id)
        
        if year:
            where_clause.append("s.ST_Year = %s")
            params.append(year)
        
        where_sql = " AND ".join(where_clause)
        if where_sql:
            where_sql = "WHERE " + where_sql
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM score_table s {where_sql}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据
        select_sql = ", ".join(select_fields)
        sql = f"""
            SELECT {select_sql}
            FROM score_table s
            {where_sql}
            ORDER BY s.ST_id DESC
            LIMIT %s, %s
        """
        cursor.execute(sql, params + [offset, size])
        scores = cursor.fetchall()
        
        return scores, total
    except Exception as e:
        print(f"获取分数线列表错误: {str(e)}")
        return [], 0
    finally:
        cursor.close()
        conn.close()

def update_score_data(score_id, update_data):
    """更新分数线数据"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 构建更新SQL
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if value is not None:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return False
        
        set_sql = ", ".join(set_clauses)
        params.append(score_id)
        
        sql = f"UPDATE score_table SET {set_sql} WHERE ST_id = %s"
        cursor.execute(sql, params)
        conn.commit()
        
        return True
    except Exception as e:
        print(f"更新分数线数据错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_schools_list(page, size, name='', is_985='', is_211=''):
    """获取学校信息列表"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    offset = (page - 1) * size
    params = []
    where_clause = []
    
    if name:
        where_clause.append("name LIKE %s")
        params.append(f"%{name}%")
    
    if is_985:
        where_clause.append("f985 = %s")
        params.append(is_985)
    
    if is_211:
        where_clause.append("f211 = %s")
        params.append(is_211)
    
    where_sql = " AND ".join(where_clause)
    if where_sql:
        where_sql = "WHERE " + where_sql
    
    try:
        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM school_info {where_sql}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据 - 根据实际表结构调整选择的字段
        sql = f"""
            SELECT school_id, name, belong, f985, f211, 
                   address, site, email, phone, province_id,
                   code_enroll, is_recruitment, create_date, area
            FROM school_info
            {where_sql}
            ORDER BY school_id
            LIMIT %s, %s
        """
        cursor.execute(sql, params + [offset, size])
        schools = cursor.fetchall()
        
        return schools, total
    except Exception as e:
        print(f"获取学校信息列表错误: {str(e)}")
        return [], 0
    finally:
        cursor.close()
        conn.close()

def update_school_data(school_id, update_data):
    """更新学校信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 构建更新SQL
        set_clauses = []
        params = []
        
        # 只更新允许的字段
        allowed_fields = ['name', 'belong', 'f985', 'f211', 'address', 
                          'site', 'email', 'phone', 'province_id', 'area']
        
        for key, value in update_data.items():
            if key in allowed_fields and value is not None:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return False
        
        set_sql = ", ".join(set_clauses)
        params.append(school_id)
        
        sql = f"UPDATE school_info SET {set_sql} WHERE school_id = %s"
        cursor.execute(sql, params)
        conn.commit()
        
        return True
    except Exception as e:
        print(f"更新学校信息错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_recommendation_histories(page, size, user_id=''):
    """获取推荐历史列表"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    offset = (page - 1) * size
    params = []
    where_clause = []
    
    if user_id:
        where_clause.append("r.user_id = %s")
        params.append(user_id)
    
    where_sql = " AND ".join(where_clause)
    if where_sql:
        where_sql = "WHERE " + where_sql
    
    try:
        # 查询总数
        count_sql = f"""
            SELECT COUNT(*) as total 
            FROM recommendation_history r
            JOIN py_user u ON r.user_id = u.id
            {where_sql}
        """
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']
        
        # 查询数据
        sql = f"""
            SELECT r.id, r.user_id, u.username, r.create_time, r.recommendations
            FROM recommendation_history r
            JOIN py_user u ON r.user_id = u.id
            {where_sql}
            ORDER BY r.create_time DESC
            LIMIT %s, %s
        """
        cursor.execute(sql, params + [offset, size])
        histories = cursor.fetchall()
        
        # 解析 JSON 字段
        for history in histories:
            try:
                history['recommendations_data'] = json.loads(history['recommendations'])
                # 只保留前3条推荐记录用于显示
                if history['recommendations_data'] and len(history['recommendations_data']) > 3:
                    history['display_recommendations'] = history['recommendations_data'][:3]
                else:
                    history['display_recommendations'] = history['recommendations_data']
            except:
                history['recommendations_data'] = []
                history['display_recommendations'] = []
        
        return histories, total
    except Exception as e:
        print(f"获取推荐历史列表错误: {str(e)}")
        return [], 0
    finally:
        cursor.close()
        conn.close() 