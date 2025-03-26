from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from utils import send_email

app = Flask(__name__)
CORS(app)

# 配置上传文件夹和允许的扩展名
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 数据库配置（请将DATABASE_URL替换为Railway提供的PostgreSQL连接字符串）
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:XdlibJgxZnCzvkTNlcXtmlKZJrHGTmPf@shuttle.proxy.rlwy.net:22849/railway")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db = SQLAlchemy(app)

from models import MenuItem

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/menu", methods=["GET"])
def get_menu():
    menu = MenuItem.query.all()
    return jsonify([{"id": item.id, "name": item.name, "image_url": item.image_url} for item in menu])

@app.route("/add_item", methods=["POST"])
def add_item():
    name = request.form.get("name")
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    file = request.files["image"]
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        image_url = f"/static/uploads/{filename}"
    else:
        return jsonify({"error": "Invalid file type"}), 400

    new_item = MenuItem(name=name, image_url=image_url)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Item added"}), 201

@app.route("/checkout", methods=["POST"])
def checkout():
    data = request.json
    email = data["email"]
    order_list = "\n".join(data["order_items"])
    send_email(email, order_list)
    return jsonify({"message": "Order placed and email sent!"})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
