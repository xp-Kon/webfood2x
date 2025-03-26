import os
from flask import Flask, request, jsonify, render_template, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.utils import secure_filename
from io import BytesIO
from utils import send_email

app = Flask(__name__)
CORS(app)

# 数据库配置，请将 DATABASE_URL 替换为 Railway 提供的 PostgreSQL 连接字符串
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:XdlibJgxZnCzvkTNlcXtmlKZJrHGTmPf@postgres.railway.internal:5432/railway")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db = SQLAlchemy(app)

from models import MenuItem

def allowed_file(filename):
    return '.' in filename

# 获取所有菜品（不包含图片数据，图片通过单独接口获取）
@app.route("/menu", methods=["GET"])
def get_menu():
    menu = MenuItem.query.all()
    return jsonify([{
        "id": item.id,
        "name": item.name,
        # 图片地址使用 /image/<id> 接口返回图片数据
        "image_url": f"/image/{item.id}"
    } for item in menu])

# 添加菜品（支持上传图片文件，将图片以二进制形式存入数据库）
@app.route("/add_item", methods=["POST"])
def add_item():
    name = request.form.get("name")
    if not name:
        return jsonify({"error": "菜品名称不能为空"}), 400

    if "image" not in request.files:
        return jsonify({"error": "未提供图片文件"}), 400
    file = request.files["image"]
    if file and allowed_file(file.filename):
        # 读取图片二进制数据和 MIME 类型
        image_data = file.read()
        image_mimetype = file.mimetype
    else:
        return jsonify({"error": "无效的文件类型"}), 400

    new_item = MenuItem(name=name, image_data=image_data, image_mimetype=image_mimetype)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "菜品添加成功"}), 201

# 获取图片数据接口，根据菜品ID返回图片
@app.route("/image/<int:item_id>", methods=["GET"])
def get_image(item_id):
    item = MenuItem.query.get_or_404(item_id)
    if not item.image_data:
        return jsonify({"error": "无图片数据"}), 404
    return send_file(BytesIO(item.image_data),
                     mimetype=item.image_mimetype,
                     as_attachment=False,
                     attachment_filename=f"item_{item_id}")

# 结算接口：提交订单并发送邮件
@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.json
    email = data["email"]
    order_list = "\n".join(data["order_items"])
    send_email(email, order_list)
    return jsonify({"message": "订单已提交，邮件已发送！"})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
