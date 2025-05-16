from flask import Blueprint, request, jsonify, session
from Dao.SchoolDao import *

school_api = Blueprint('school_api', __name__)

@school_api.route('/list', methods=['GET'])
def get_school_list():
    """获取学校列表"""
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    name = request.args.get('name', '')
    province_id = request.args.get('province_id', '')
    is_985 = request.args.get('is_985', '')
    is_211 = request.args.get('is_211', '')
    
    schools, total = get_schools(page, size, name, province_id, is_985, is_211)
    
    # 如果用户已登录，记录浏览历史
    if 'user_id' in session:
        for school in schools:
            add_view_history(session['user_id'], school['school_id'])
    
    return jsonify({
        "status": "success",
        "data": {
            "total": total,
            "schools": schools
        }
    })

@school_api.route('/detail/<int:school_id>', methods=['GET'])
def get_school_detail(school_id):
    """获取学校详情"""
    school = get_school_by_id(school_id)
    scores = get_school_scores(school_id)
    
    # 如果用户已登录，记录浏览历史
    if 'user_id' in session:
        add_view_history(session['user_id'], school_id)
    
    return jsonify({
        "status": "success",
        "data": {
            "school": school,
            "scores": scores
        }
    })

@school_api.route('/provinces', methods=['GET'])
def get_provinces():
    """获取所有省份信息"""
    provinces = get_all_provinces()
    
    return jsonify({
        "status": "success",
        "data": provinces
    })

@school_api.route('/scores', methods=['GET'])
def get_scores():
    """获取学校分数线"""
    school_id = request.args.get('school_id')
    province_id = request.args.get('province_id')
    year = request.args.get('year')
    
    scores = get_filtered_scores(school_id, province_id, year)
    
    return jsonify({
        "status": "success",
        "data": scores
    }) 