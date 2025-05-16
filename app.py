from flask import Flask, render_template, request, redirect, url_for, jsonify, session
# from Controller.dapin import *
# from Controller.admin import *
from Controller.UserAPI import *
# from Controller.data import *
# from Controller.postspl import *
from flask_cors import CORS
import sqlite3
import hashlib
import os
from Controller.RecommendAPI import recommend_api
from Controller.SchoolAPI import school_api
from Controller.AdminAPI import admin_api

app = Flask(__name__)
# 设置 secret_key 来保证 session 的安全性
app.secret_key = os.urandom(24)  # 使用随机生成的 24 字节密钥
CORS(app)
# app.register_blueprint(dapin_api, url_prefix='/dapin')
# app.register_blueprint(data_api, url_prefix='/data')
app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(admin_api, url_prefix='/admin/api')
# app.register_blueprint(sql_api, url_prefix='/sql')
app.register_blueprint(recommend_api, url_prefix='/recommend')
app.register_blueprint(school_api, url_prefix='/school')



@app.route('/login')
def hello_world():  # put application's code here
    return render_template("login.html")

@app.route('/adminHome')
def adminHome():  # put application's code here
    return render_template("base.html")
@app.route('/')
def Home():  # put application's code here
    return render_template("home.html")

@app.route('/User')
def User():  # put application's code here
    
    return render_template("userlist.html")
@app.route('/Admin')
def Admin():  # put application's code here

    return render_template("adminlist.html")
@app.route('/adduser')
def adduser():  # put application's code here
    return render_template("adduser.html")
@app.route('/addadmin')
def addadmin():  # put application's code here
    return render_template("addadmin.html")

# 添加退出登录路由
@app.route('/logout')
def logout():
    # 清除所有会话数据
    session.clear()
    # 不使用普通重定向，而是返回一个脚本，强制整个页面(顶层窗口)跳转
    return '''
    <script>
        window.top.location.href = '/login';
    </script>
    '''

@app.route('/recommend')
def recommend_page():
    return render_template("recommend.html")

@app.route('/schools')
def schools_page():
    return render_template("schools.html")

@app.route('/school_detail/<int:school_id>')
def school_detail_page(school_id):
    return render_template("school_detail.html", school_id=school_id)

@app.route('/favorites')
def favorites_page():
    return render_template("favorites.html")

@app.route('/admin/score_data')
def admin_score_data():
    return render_template("admin_score_data.html")

@app.route('/admin/school_data')
def admin_school_data():
    return render_template("admin_school_data.html")

@app.route('/admin/recommendation_history')
def admin_recommendation_history():
    return render_template("admin_recommendation_history.html")

if __name__ == '__main__':
    app.run(debug=True)

