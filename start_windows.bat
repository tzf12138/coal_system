@echo off
echo ===== 安装依赖 =====
pip install -r requirements.txt
echo ===== 数据库迁移 =====
python manage.py migrate
echo ===== 初始化演示数据 =====
python manage.py seed_demo
echo ===== 启动平台 =====
python manage.py runserver
pause
