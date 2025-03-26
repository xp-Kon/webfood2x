import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from utils import send_email
app = Flask(__name__)
CORS(app)

# 配置上传文件夹和允许上传的扩展名
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 数据库配置（使用 Railway 提供的 PostgreSQL 数据库）
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:XdlibJgxZnCzvkTNlcXtmlKZJrHGTmPf@postgres.railway.internal:5432/railway")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db = SQLAlchemy(app)
db.init_app(app)
from models import MenuItem

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 获取所有菜品
@app.route("/menu", methods=["GET"])
def get_menu():
    menu = MenuItem.query.all()
    return jsonify([{"id": item.id, "name": item.name, "image_url": item.image_url} for item in menu])

# 添加菜品（支持上传图片文件）
@app.route("/add_item", methods=["POST"])
def add_item():
    # 菜品名称从表单中获取
    name = request.form.get("name")
    # 处理上传文件
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    file = request.files["image"]
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        # 生成图片URL（生产环境请使用静态资源托管服务或Railway的静态文件托管）
        image_url = f"/static/uploads/{filename}"
    else:
        return jsonify({"error": "Invalid file type"}), 400

    new_item = MenuItem(name=name, image_url=image_url)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Item added"}), 201

# 结算并发送订单邮件
@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.json
    email = data["email"]
    order_list = "\n".join(data["order_items"])
    send_email(email, order_list)
    return jsonify({"message": "Order placed and email sent!"})

# 后端调试页面（可选）
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # 开发时在本地运行
    app.run(debug=True)
