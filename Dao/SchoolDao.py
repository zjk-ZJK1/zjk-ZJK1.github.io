import pymysql
from Dao.UserDao import get_connection

def get_schools(page, size, name='', province_id='', is_985='', is_211=''):
    """获取学校列表"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    offset = (page - 1) * size
    params = []
    where_clause = []
    
    if name:
        where_clause.append("name LIKE %s")
        params.append(f"%{name}%")
    
    if province_id:
        where_clause.append("province_id = %s")
        params.append(province_id)
    
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
        
        # 查询数据
        sql = f"""
            SELECT school_id, name, belong, f985, f211, 
                   province_id, address, site, email, phone
            FROM school_info
            {where_sql}
            ORDER BY school_id
            LIMIT %s, %s
        """
        cursor.execute(sql, params + [offset, size])
        schools = cursor.fetchall()
        
        return schools, total
    except Exception as e:
        print(f"获取学校列表错误: {str(e)}")
        return [], 0
    finally:
        cursor.close()
        conn.close()

def get_school_by_id(school_id):
    """根据ID获取学校详情"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            """SELECT * FROM school_info WHERE school_id = %s""",
            (school_id,)
        )
        school = cursor.fetchone()
        
        # 获取学校图片
        if school:
            cursor.execute(
                """SELECT * FROM school_index WHERE SI_id = %s""",
                (school_id,)
            )
            images = cursor.fetchone()
            if images:
                school['images'] = {
                    'img_1': images['Img_1'],
                    'img_2': images['Img_2'],
                    'img_3': images['Img_3'],
                    'img_4': images['Img_4'],
                    'img_5': images['Img_5'],
                    'img_6': images['Img_6'],
                    'img_name': images['Img_name']
                }
        
        return school
    except Exception as e:
        print(f"获取学校详情错误: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_school_scores(school_id):
    """获取学校分数线"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            """SELECT * FROM score_table
               WHERE SI_id = %s
               ORDER BY ST_Year DESC, Pro_id""",
            (school_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"获取学校分数线错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_view_history(user_id, school_id):
    """添加用户浏览历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO user_view_history (user_id, school_id, view_time)
               VALUES (%s, %s, NOW())""",
            (user_id, school_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"添加浏览历史错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_all_provinces():
    """获取所有省份信息"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 检查字段名
        cursor.execute("DESCRIBE score_table")
        columns = cursor.fetchall()
        province_column = None
        
        # 查找包含"province"的字段
        for col in columns:
            if 'province' in col['Field'].lower():
                province_column = col['Field']
                break
        
        if not province_column:
            # 如果没有找到省份字段，直接返回空列表
            print("警告：未找到省份字段")
            return []
            
        # 使用找到的字段名
        cursor.execute(f"""
            SELECT DISTINCT {province_column} as id, {province_column} as name 
            FROM score_table 
            WHERE {province_column} IS NOT NULL
            ORDER BY {province_column}
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"获取省份信息错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_filtered_scores(school_id=None, province_id=None, year=None):
    """获取筛选后的分数线"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    where_clause = []
    params = []
    
    if school_id:
        where_clause.append("SI_id = %s")
        params.append(school_id)
    
    if province_id:
        where_clause.append("ST_province_id = %s")
        params.append(province_id)
    
    if year:
        where_clause.append("ST_Year = %s")
        params.append(year)
    
    where_sql = " AND ".join(where_clause)
    if where_sql:
        where_sql = "WHERE " + where_sql
    
    try:
        sql = f"""
            SELECT * FROM score_table
            {where_sql}
            ORDER BY ST_Year DESC, ST_Min DESC
            LIMIT 1000
        """
        cursor.execute(sql, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"获取筛选分数线错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_schools_by_score(score, subject_type=None, preferences=None):
    """根据分数和偏好获取学校推荐（优化版）"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 基本查询条件：分数在合适范围内
        base_where = "s.ST_Min <= %s"
        params = [score]
        
        # 添加科目类型过滤
        if subject_type:
            base_where += " AND s.ST_Type = %s"
            params.append(subject_type)
        
        # 添加偏好过滤
        preference_where = ""
        if preferences:
            preference_conditions = []
            for pref in preferences:
                if pref == '985':
                    preference_conditions.append("si.f985 = '1'")
                elif pref == '211':
                    preference_conditions.append("si.f211 = '1'")
            
            if preference_conditions:
                preference_where = " AND (" + " OR ".join(preference_conditions) + ")"
        
        # 构建基本查询 - 使用SELECT时只选择必要字段
        query = f"""
            SELECT DISTINCT 
                si.school_id, 
                si.name, 
                si.belong, 
                si.f985, 
                si.f211, 
                si.address, 
                si.site, 
                s.ST_Min as min_score, 
                s.ST_Average as avg_score, 
                s.ST_Max as max_score,
                s.ST_Type, 
                s.ST_Local_batch_name,
                {score} - s.ST_Min as score_diff
            FROM score_table s
            JOIN school_info si ON s.SI_id = si.school_id
            WHERE {base_where} {preference_where}
            ORDER BY ABS(s.ST_Min - {score}) ASC
            LIMIT 20
        """
        
        # 执行查询
        cursor.execute(query, params)
        schools = cursor.fetchall()
        
        # 计算匹配度 - 使用更高效的算法
        for school in schools:
            score_diff = school.get('score_diff', 0)
            
            # 简化匹配度计算逻辑
            if score_diff < 0:
                similarity = 10
            elif score_diff <= 30:
                # 线性计算在合理范围内的匹配度
                similarity = 85 - (score_diff / 30) * 20
            else:
                # 超出太多则固定较低匹配度
                similarity = 65 - min((score_diff - 30) / 10, 25)
            
            # 985/211院校加分 - 合并计算更高效
            if school.get('f985') == '1':
                similarity += (5 if '985' in preferences else 3)
            elif school.get('f211') == '1':
                similarity += (5 if '211' in preferences else 2)
            
            # 确保匹配度范围在0-100之间
            similarity = min(max(round(similarity), 0), 100)
            school['similarity'] = similarity
            
            # 重命名字段以匹配前端期望
            school['ST_Min'] = school.pop('min_score', 0)
            school['ST_Average'] = school.pop('avg_score', 0)
            school['ST_Max'] = school.pop('max_score', 0)
            
            # 删除中间计算字段
            if 'score_diff' in school:
                del school['score_diff']
        
        # 按匹配度排序
        schools.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        # 限制返回数量
        return schools[:12]
    except Exception as e:
        print(f"获取学校推荐错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_favorite(user_id, school_id):
    """将学校添加到用户收藏"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 检查是否已经收藏
        cursor.execute(
            "SELECT id FROM user_favorites WHERE user_id = %s AND school_id = %s",
            (user_id, school_id)
        )
        if cursor.fetchone():
            return False  # 已经收藏过了
        
        # 添加收藏
        cursor.execute(
            "INSERT INTO user_favorites (user_id, school_id, create_time) VALUES (%s, %s, NOW())",
            (user_id, school_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"添加收藏错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_favorites(user_id):
    """获取用户收藏的学校列表"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            """
            SELECT f.id as favorite_id, f.create_time, 
                   s.school_id, s.name, s.belong, s.f985, s.f211, s.address
            FROM user_favorites f
            JOIN school_info s ON f.school_id = s.school_id
            WHERE f.user_id = %s
            ORDER BY f.create_time DESC
            """,
            (user_id,)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"获取用户收藏错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def remove_favorite_school(user_id, favorite_id):
    """删除用户收藏的学校"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM user_favorites WHERE id = %s AND user_id = %s",
            (favorite_id, user_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"删除收藏错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close() 