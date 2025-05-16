from flask import Blueprint, request, jsonify, session
from Dao.RecommendDao import *
from Service.RecommendService import *
from Dao.SchoolDao import get_schools_by_score
import json
import time
import hashlib
from functools import lru_cache

recommend_api = Blueprint('recommend_api', __name__)

# 内存缓存，用于存储推荐结果
recommendation_cache = {}

@recommend_api.route('/submit_info', methods=['POST'])
def submit_info():
    """提交高考信息"""
    # 不再严格检查登录状态，测试阶段允许未登录用户使用
    # if 'user_id' not in session:
    #     return jsonify({"status": "error", "message": "请先登录"}), 401
    
    try:
        data = request.json
        score = data.get('score')
        subject_type = data.get('subject_type')
        batch = data.get('batch')
        preferences = data.get('preferences', [])
        
        # 验证必填数据
        if not score or not subject_type or not batch:
            return jsonify({"status": "error", "message": "请填写所有必填信息"}), 400
        
        # 保存到会话中，以便推荐时使用
        session['exam_info'] = {
            'score': score,
            'subject_type': subject_type,
            'batch': batch,
            'preferences': preferences
        }
        
        return jsonify({"status": "success", "message": "信息提交成功"})
    except Exception as e:
        print(f"提交信息错误: {str(e)}")
        return jsonify({"status": "error", "message": "服务器错误，请稍后重试"}), 500

# 使用LRU缓存装饰器优化学校推荐查询
@lru_cache(maxsize=100)
def get_cached_schools(score, subject_type, preferences_key):
    """带缓存的学校推荐查询"""
    preferences = json.loads(preferences_key) if preferences_key else []
    return get_schools_by_score(score, subject_type, preferences)

@recommend_api.route('/get_recommendations', methods=['GET', 'POST'])
def get_recommendations():
    """获取推荐结果"""
    start_time = time.time()  # 记录开始时间
    
    try:
        if request.method == 'POST':
            data = request.json
            score = data.get('score')
            subject_type = data.get('subject_type')
            preferences = data.get('preferences', [])
        else:
            # 从会话获取
            if 'exam_info' not in session:
                return jsonify({"status": "error", "message": "请先提交高考信息"}), 400
            
            exam_info = session['exam_info']
            score = exam_info.get('score')
            subject_type = exam_info.get('subject_type')
            preferences = exam_info.get('preferences', [])
        
        # 生成缓存键
        cache_key = f"{score}_{subject_type}_{json.dumps(sorted(preferences))}"
        
        # 检查缓存
        if cache_key in recommendation_cache:
            schools = recommendation_cache[cache_key]
            print(f"从缓存获取推荐结果，用时: {time.time() - start_time:.3f}秒")
        else:
            # 使用LRU缓存的函数获取推荐
            preferences_key = json.dumps(sorted(preferences)) if preferences else None
            schools = get_cached_schools(score, subject_type, preferences_key)
            
            # 存入缓存(最多保留300个缓存项)
            if len(recommendation_cache) > 300:
                # 清理最早的100个缓存项
                keys_to_remove = list(recommendation_cache.keys())[:100]
                for key in keys_to_remove:
                    recommendation_cache.pop(key, None)
            
            recommendation_cache[cache_key] = schools
            print(f"生成推荐结果，用时: {time.time() - start_time:.3f}秒")
        
        # 保存到会话中，用于后续保存
        session['recommendations'] = json.dumps(schools)
        
        end_time = time.time()
        print(f"推荐API总耗时: {end_time - start_time:.3f}秒")
        
        return jsonify({
            "status": "success", 
            "data": schools
        })
    except Exception as e:
        print(f"获取推荐错误: {str(e)}")
        return jsonify({"status": "error", "message": "服务器错误，请稍后重试"}), 500

@recommend_api.route('/save_recommendation', methods=['POST'])
def save_recommendation():
    """保存推荐结果"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    
    try:
        # 检查是否有推荐结果
        if 'recommendations' not in session:
            return jsonify({"status": "error", "message": "没有可保存的推荐结果"}), 400
        
        from Dao.RecommendDao import save_recommendation_history
        
        user_id = session.get('user_id')
        recommendations = session.get('recommendations')
        
        # 保存推荐历史
        success = save_recommendation_history(user_id, recommendations)
        
        if success:
            return jsonify({"status": "success", "message": "推荐结果保存成功"})
        else:
            return jsonify({"status": "error", "message": "保存失败"}), 500
    except Exception as e:
        print(f"保存推荐结果错误: {str(e)}")
        return jsonify({"status": "error", "message": "服务器错误，请稍后重试"}), 500

@recommend_api.route('/save_favorite', methods=['POST'])
def save_favorite():
    """收藏学校"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    
    try:
        data = request.json
        school_id = data.get('school_id')
        
        if not school_id:
            return jsonify({"status": "error", "message": "学校ID不能为空"}), 400
        
        from Dao.SchoolDao import add_favorite
        
        user_id = session.get('user_id')
        success = add_favorite(user_id, school_id)
        
        if success:
            return jsonify({"status": "success", "message": "收藏成功"})
        else:
            return jsonify({"status": "error", "message": "收藏失败，可能已经收藏过该学校"}), 500
    except Exception as e:
        print(f"收藏学校错误: {str(e)}")
        return jsonify({"status": "error", "message": "服务器错误，请稍后重试"}), 500

@recommend_api.route('/get_favorites', methods=['GET'])
def get_favorites():
    """获取用户收藏的学校"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    
    user_id = session['user_id']
    favorites = get_user_favorites(user_id)
    
    return jsonify({
        "status": "success", 
        "data": {
            "favorites": favorites
        }
    })

@recommend_api.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    """取消收藏学校"""
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "请先登录"}), 401
    
    user_id = session['user_id']
    data = request.json
    favorite_id = data.get('favorite_id')
    
    result = remove_favorite_school(user_id, favorite_id)
    
    if result:
        return jsonify({"status": "success", "message": "取消收藏成功"})
    else:
        return jsonify({"status": "error", "message": "取消收藏失败"}), 400 