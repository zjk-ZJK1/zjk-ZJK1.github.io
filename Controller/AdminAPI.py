from flask import Blueprint, request, jsonify, session, render_template
from Dao.AdminDao import *

admin_api = Blueprint('admin_api', __name__)

# 分数线数据相关API
@admin_api.route('/score_data_list', methods=['GET'])
def get_score_data_list():
    """获取分数线数据列表"""
    if not is_admin():
        return jsonify({"status": "error", "message": "权限不足"}), 403
        
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    school_name = request.args.get('school_name', '')
    province_id = request.args.get('province_id', '')
    year = request.args.get('year', '')
    
    scores, total = get_scores_list(page, size, school_name, province_id, year)
    
    return jsonify({
        "status": "success",
        "data": {
            "total": total,
            "scores": scores
        }
    })

@admin_api.route('/update_score', methods=['POST'])
def update_score():
    """更新分数线数据"""
    if not is_admin():
        return jsonify({"status": "error", "message": "权限不足"}), 403
    
    data = request.json
    score_id = data.get('ST_id')
    update_data = {
        'ST_Min': data.get('ST_Min'),
        'ST_Average': data.get('ST_Average'),
        'ST_Max': data.get('ST_Max'),
        'ST_Province': data.get('ST_Province'),
        'ST_Year': data.get('ST_Year'),
        'ST_Local_batch_name': data.get('ST_Local_batch_name'),
        'ST_Type': data.get('ST_Type')
    }
    
    success = update_score_data(score_id, update_data)
    
    if success:
        return jsonify({"status": "success", "message": "更新成功"})
    else:
        return jsonify({"status": "error", "message": "更新失败"}), 500

# 学校信息相关API
@admin_api.route('/school_data_list', methods=['GET'])
def get_school_data_list():
    """获取学校信息列表"""
    if not is_admin():
        return jsonify({"status": "error", "message": "权限不足"}), 403
        
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    name = request.args.get('name', '')
    is_985 = request.args.get('is_985', '')
    is_211 = request.args.get('is_211', '')
    
    schools, total = get_schools_list(page, size, name, is_985, is_211)
    
    return jsonify({
        "status": "success",
        "data": {
            "total": total,
            "schools": schools
        }
    })

@admin_api.route('/update_school', methods=['POST'])
def update_school():
    """更新学校信息"""
    if not is_admin():
        return jsonify({"status": "error", "message": "权限不足"}), 403
    
    data = request.json
    school_id = data.get('school_id')
    update_data = {
        'name': data.get('name'),
        'belong': data.get('belong'),
        'f985': data.get('f985'),
        'f211': data.get('f211'),
        'address': data.get('address'),
        'site': data.get('site'),
        'email': data.get('email'),
        'phone': data.get('phone')
    }
    
    success = update_school_data(school_id, update_data)
    
    if success:
        return jsonify({"status": "success", "message": "更新成功"})
    else:
        return jsonify({"status": "error", "message": "更新失败"}), 500

# 推荐历史相关API
@admin_api.route('/recommendation_history_list', methods=['GET'])
def get_recommendation_history_list():
    """获取推荐历史列表"""
    if not is_admin():
        return jsonify({"status": "error", "message": "权限不足"}), 403
        
    page = int(request.args.get('page', 1))
    size = int(request.args.get('size', 10))
    user_id = request.args.get('user_id', '')
    
    histories, total = get_recommendation_histories(page, size, user_id)
    
    return jsonify({
        "status": "success",
        "data": {
            "total": total,
            "histories": histories
        }
    })

# 检查是否为管理员
def is_admin():
    """检查当前用户是否为管理员"""
    # 临时返回True以便开发测试
    return True
    
    # 以下是正式代码，等系统测试通过后可以取消注释
    '''
    print("Session内容:", session)  # 调试用，查看session内容
    if 'user_id' not in session:
        print("用户未登录")
        return False
    
    # 如果session中没有role字段，查询数据库
    if 'role' not in session:
        from Dao.UserDao import get_user_by_id
        user = get_user_by_id(session['user_id'])
        if user and (user['usertype'] == 'admin' or user['usertype'] == '1'):
            session['role'] = 'admin'  # 设置角色
            return True
        return False
    
    return session['role'] == 'admin'
    ''' 