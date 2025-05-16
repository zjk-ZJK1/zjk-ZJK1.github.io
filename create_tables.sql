-- 用户高考信息表
CREATE TABLE user_exam_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    score INT NOT NULL,
    province_id INT NOT NULL,
    subject_type VARCHAR(20) NOT NULL COMMENT '文科/理科',
    batch VARCHAR(50) NOT NULL COMMENT '批次',
    preferences TEXT COMMENT '偏好JSON',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY (user_id),
    FOREIGN KEY (user_id) REFERENCES py_user(id)
);

-- 用户收藏学校表
CREATE TABLE user_favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    school_id INT NOT NULL,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY (user_id, school_id),
    FOREIGN KEY (user_id) REFERENCES py_user(id)
);

-- 用户浏览历史表
CREATE TABLE user_view_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    school_id INT NOT NULL,
    view_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES py_user(id)
);

-- 推荐结果历史表
CREATE TABLE recommendation_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    recommendations TEXT COMMENT 'JSON格式推荐结果',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES py_user(id)
); 