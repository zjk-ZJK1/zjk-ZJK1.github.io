import pymysql
from Dao.UserDao import get_connection
import json

def save_user_exam_info(user_id, score, province_id, subject_type, batch, preferences):
    """保存用户高考信息"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 首先检查是否已存在记录
        cursor.execute(
            "SELECT id FROM user_exam_info WHERE user_id = %s", 
            (user_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录
            cursor.execute(
                """UPDATE user_exam_info 
                   SET score = %s, province_id = %s, subject_type = %s, 
                       batch = %s, preferences = %s 
                   WHERE user_id = %s""",
                (score, province_id, subject_type, batch, str(preferences), user_id)
            )
        else:
            # 创建新记录
            cursor.execute(
                """INSERT INTO user_exam_info 
                   (user_id, score, province_id, subject_type, batch, preferences) 
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_id, score, province_id, subject_type, batch, str(preferences))
            )
        
        conn.commit()
        return True
    except Exception as e:
        print(f"保存用户高考信息错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_exam_info(user_id):
    """获取用户高考信息"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            """SELECT * FROM user_exam_info WHERE user_id = %s""",
            (user_id,)
        )
        return cursor.fetchone()
    except Exception as e:
        print(f"获取用户高考信息错误: {str(e)}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_similar_score_schools(score, province_id, subject_type, batch, limit=50):
    """获取与用户分数相近的学校"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询与用户分数相近的学校
        cursor.execute(
            """SELECT s.SI_id, s.ST_School_name, s.ST_Min, s.ST_Average, s.ST_Max, 
                      s.ST_Type, s.ST_Local_batch_name
               FROM score_table s
               WHERE s.Pro_id = %s 
                 AND s.ST_Type LIKE %s
                 AND s.ST_Local_batch_name LIKE %s
                 AND s.ST_Min <= %s
                 AND s.ST_Min >= %s
               ORDER BY ABS(s.ST_Min - %s)
               LIMIT %s""",
            (province_id, f"%{subject_type}%", f"%{batch}%", 
             score + 20, score - 50, score, limit)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"获取相似分数学校错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_favorite_school(user_id, school_id):
    """添加用户收藏的学校"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 检查是否已收藏
        cursor.execute(
            "SELECT id FROM user_favorites WHERE user_id = %s AND school_id = %s", 
            (user_id, school_id)
        )
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO user_favorites (user_id, school_id, create_time) VALUES (%s, %s, NOW())",
                (user_id, school_id)
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"添加收藏学校错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def get_user_favorites(user_id):
    """获取用户收藏的学校"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            """SELECT f.id, f.school_id, s.name, s.f985, s.f211, 
                      s.address, s.site, f.create_time
               FROM user_favorites f
               JOIN school_info s ON f.school_id = s.school_id
               WHERE f.user_id = %s
               ORDER BY f.create_time DESC""",
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
        # 确保只能删除自己的收藏
        cursor.execute(
            "DELETE FROM user_favorites WHERE id = %s AND user_id = %s", 
            (favorite_id, user_id)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"删除收藏学校错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def save_recommendation_history(user_id, recommendations):
    """保存推荐结果历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # 将推荐结果转为JSON字符串
        recommendations_json = json.dumps(recommendations)
        
        cursor.execute(
            "INSERT INTO recommendation_history (user_id, recommendations, create_time) VALUES (%s, %s, NOW())",
            (user_id, recommendations_json)
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"保存推荐历史错误: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close() 