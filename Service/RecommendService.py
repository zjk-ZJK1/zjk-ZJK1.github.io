from Dao.RecommendDao import *
import numpy as np
from collections import Counter

def get_collaborative_filtering_recommendations(user_info):
    """使用协同过滤算法获取推荐"""
    user_id = user_info['user_id']
    score = user_info['score']
    province_id = user_info['province_id']
    subject_type = user_info['subject_type']
    batch = user_info['batch']
    
    # 1. 获取与用户分数相近的学校
    similar_schools = get_similar_score_schools(score, province_id, subject_type, batch)
    
    # 2. 获取相似用户的收藏和浏览历史
    similar_users = get_similar_users(user_id, score, province_id, subject_type)
    
    # 3. 基于相似用户的行为推荐学校
    user_preferences = {}
    for user in similar_users:
        # 获取该用户的收藏
        favorites = get_user_favorites(user['user_id'])
        for fav in favorites:
            school_id = fav['school_id']
            user_preferences[school_id] = user_preferences.get(school_id, 0) + 2  # 收藏权重加2
        
        # 获取该用户的浏览历史
        history = get_user_view_history(user['user_id'])
        for hist in history:
            school_id = hist['school_id']
            user_preferences[school_id] = user_preferences.get(school_id, 0) + 1  # 浏览权重加1
    
    # 4. 计算最终推荐分数
    recommendations = []
    for school in similar_schools:
        school_id = school['SI_id']
        base_score = 100 - abs(school['ST_Min'] - score)  # 分数匹配度
        preference_score = user_preferences.get(school_id, 0) * 10  # 协同过滤权重
        
        final_score = base_score + preference_score
        
        school['recommendation_score'] = final_score
        recommendations.append(school)
    
    # 5. 按推荐分数排序
    recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
    
    return recommendations[:20]  # 返回前20所推荐学校

def get_similar_users(user_id, score, province_id, subject_type, limit=20):
    """获取与当前用户相似的用户"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 查询与用户条件相似的其他用户
        cursor.execute(
            """SELECT u.user_id, u.score, u.province_id, u.subject_type,
                      ABS(u.score - %s) as score_diff
               FROM user_exam_info u
               WHERE u.user_id != %s
                 AND u.province_id = %s
                 AND u.subject_type = %s
                 AND ABS(u.score - %s) < 50
               ORDER BY score_diff
               LIMIT %s""",
            (score, user_id, province_id, subject_type, score, limit)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"获取相似用户错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_user_view_history(user_id, limit=50):
    """获取用户浏览历史"""
    conn = get_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(
            """SELECT * FROM user_view_history 
               WHERE user_id = %s
               ORDER BY view_time DESC
               LIMIT %s""",
            (user_id, limit)
        )
        return cursor.fetchall()
    except Exception as e:
        print(f"获取用户浏览历史错误: {str(e)}")
        return []
    finally:
        cursor.close()
        conn.close() 