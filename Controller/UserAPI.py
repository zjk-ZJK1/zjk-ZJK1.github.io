from flask import Blueprint, jsonify, request, render_template, session
from Dao.UserDao import *
import pymysql

# from urllib import request
from flask import Blueprint,jsonify,request

user_api= Blueprint('user_api', __name__)


@user_api.route('/loginApi', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(data)
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        # 验证必填参数
        if not all([username, password, role]):
            return jsonify({
                'msg': '请填写所有必填项',
                'code': 400
            })
            
        res = loginDao(username, password, role)
        
        if res and len(res) > 0:
            body = {
                'id': res[0][0],
                'username': res[0][1],
                'password': res[0][2],
                'nickname': res[0][3],
                'sex': res[0][4],
                'age': res[0][5],
                'phone': res[0][6],
                'email': res[0][7],
                'brithday': res[0][8],
                'card': res[0][9],
                'content': res[0][10],
                'remarks': res[0][11],
                'role': '管理员' if role == 'admin' else '用户',
                'token': res[0][0]
            }
            
            # 将用户信息保存到 session 中
            session['user_id'] = body['id']
            session['username'] = body['username']
            session['role'] = body['role']
            session['nickname'] = body['nickname']
            session['logged_in'] = True
            
            # 设置用户角色
            if body['role'] == 'admin':
                session['role'] = 'admin'
            else:
                session['role'] = 'user'
            
            return jsonify({
                'msg': '登录成功',
                'data': body,
                'code': 200
            })
        else:
            return jsonify({
                'msg': '账号或密码不正确',
                'code': 400
            })
            
    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({
            'msg': '登录失败，请稍后重试',
            'code': 500
        })

@user_api.route('/logout', methods=['POST', 'GET'])
def logout():
    # 清除 session 中的用户信息
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('nickname', None)
    session.pop('logged_in', None)
    
    return jsonify({
        'msg': '退出登录成功',
        'code': 200
    })

@user_api.route('/checkLogin', methods=['GET'])
def check_login():
    if session.get('logged_in'):
        user_data = {
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'role': session.get('role'),
            'nickname': session.get('nickname'),
        }
        return jsonify({
            'code': 200,
            'msg': '用户已登录',
            'data': user_data
        })
    else:
        return jsonify({
            'code': 401,
            'msg': '用户未登录'
        })

@user_api.route('/registerApi', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        email = data.get('email')
        role = data.get('role', 'user')  # 默认为普通用户
        
        # 验证必填字段
        if not all([username, password, phone, email]):
            return jsonify({
                'code': 400,
                'message': '请填写所有必填项'
            })
            
        # 检查用户名是否已存在
        if GetuserDao(username):
            return jsonify({
                'code': 400,
                'message': '用户名已存在'
            })
            
        # 调用 DAO 层注册方法
        Addregister(username, password,role)
        
        return jsonify({
            'code': 200,
            'message': '注册成功'
        })
        
    except Exception as e:
        print(f"注册错误: {str(e)}")
        return jsonify({
            'code': 500,
            'message': '注册失败，请稍后重试'
        })

@user_api.route('/userlist' , methods=[ 'POST'])
def getuserlist():
    data = request.get_json()
    username = data.get('username')
    page = data.get('page', 1)
    limit = data.get('limit', 20)
    res = ListDao(username=username, page=page, limit=limit)
    data = res['data']
    datalist=[]
    for user in data:
        print(user)
        body = {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'nickname': user[3],
            'sex': user[4],
            'age': user[5],
            'phone': user[6],
            'email': user[7],
            'brithday': user[8],
            'card': user[9],
            'content': user[10],
            'remarks': user[11],
            'role': user[12],
            'token': user[0]
        }
        datalist.append(body)
    data = {
        'msg': '查询成功',
        'data': datalist,
        'code': 200
        }

    return jsonify(data)
@user_api.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    try:
        DeleteUserDao(id)
        return jsonify({
            'msg': '删除成功',
            'code': 200
        })
    except Exception as e:
        return jsonify({
            'msg': '删除失败',
            'code': 500
        })


@user_api.route('/add', methods=['POST'])
def add_user():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname')
        sex = data.get('sex')
        age = data.get('age')
        phone = data.get('phone')
        email = data.get('email')
        birthday = data.get('birthday')
        card = data.get('card')
        content = data.get('content')
        remarks = data.get('remarks')

        AddUserDao(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks)
        return jsonify({
            'msg': '添加成功',
            'code': 200
        })
    except Exception as e:
        return jsonify({
            'msg': '添加失败', 
            'code': 500
        })

@user_api.route('/edituser')
def edit_user_page():
    user_id = request.args.get('id')
    user_tuple = get_user_by_id(user_id)
    # 将元组转换为字典
    user = {
        'id': user_tuple[0],
        'username': user_tuple[1],
        'password': user_tuple[2],
        'nickname': user_tuple[3],
        'sex': user_tuple[4],
        'age': user_tuple[5],
        'phone': user_tuple[6],
        'email': user_tuple[7]
    }
    print("用户数据:", user)  # 添加调试输出
    return render_template('edituser.html', user=user)

@user_api.route('/edit', methods=['POST'])
def edit_user():
    data = request.get_json()
    try:
        user_id = data.get('id')
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname')
        sex = data.get('sex')
        age = data.get('age')
        phone = data.get('phone')
        email = data.get('email')
        
        # 更新用户信息
        success = update_user(user_id, username, password, nickname, sex, age, phone, email)
        
        if success:
            return jsonify({"code": 200, "message": "更新成功"})
        else:
            return jsonify({"code": 500, "message": "更新失败"})
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)})
    
@user_api.route('/adminlist' , methods=[ 'POST'])
def getadminlist():
    data = request.get_json()
    username = data.get('username')
    page = data.get('page', 1)
    limit = data.get('limit', 20)
    res = ListAdminDao(username=username, page=page, limit=limit)
    data = res['data']
    datalist=[]
    for user in data:
        print(user)
        body = {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'nickname': user[3],
            'sex': user[4],
            'age': user[5],
            'phone': user[6],
            'email': user[7],
            'brithday': user[8],
            'card': user[9],
            'content': user[10],
            'remarks': user[11],
            'role': user[12],
            'token': user[0]
        }
        datalist.append(body)
    data = {
        'msg': '查询成功',
        'data': datalist,
        'code': 200
        }

    return jsonify(data)
@user_api.route('/addadmin', methods=['POST'])
def add_admin():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        nickname = data.get('nickname')
        sex = data.get('sex')
        age = data.get('age')
        phone = data.get('phone')
        email = data.get('email')
        birthday = data.get('birthday')
        card = data.get('card')
        content = data.get('content')
        remarks = data.get('remarks')

        AddAdminDao(username, password, nickname, sex, age, phone, email, birthday, card, content, remarks)
        return jsonify({
            'msg': '添加成功',
            'code': 200
        })
    except Exception as e:
        return jsonify({
            'msg': '添加失败',
            'code': 500
        })

@user_api.route('/getUserInfo', methods=['GET'])
def get_user_info():
    try:
        user_id = request.args.get('id')
        if not user_id:
            return jsonify({
                'code': 400,
                'msg': '缺少用户ID参数'
            })
            
        # 检查是否是当前登录用户请求自己的信息
        if session.get('logged_in') and str(session.get('user_id')) == str(user_id):
            # 获取用户信息
            user_info = get_user_by_id(user_id)
            
            if user_info:
                data = {
                    'id': user_info[0],
                    'username': user_info[1],
                    'nickname': user_info[3],
                    'sex': user_info[4],
                    'age': user_info[5],
                    'phone': user_info[6],
                    'email': user_info[7],
                    'brithday': user_info[8],
                    'card': user_info[9],
                    'content': user_info[10],
                    'remarks': user_info[11],
                    'role': session.get('role')
                }
                
                return jsonify({
                    'code': 200,
                    'msg': '获取用户信息成功',
                    'data': data
                })
            else:
                return jsonify({
                    'code': 404,
                    'msg': '用户不存在'
                })
        else:
            return jsonify({
                'code': 403,
                'msg': '无权访问此用户信息'
            })
            
    except Exception as e:
        print(f"获取用户信息错误: {str(e)}")
        return jsonify({
            'code': 500,
            'msg': '获取用户信息失败'
        })

  