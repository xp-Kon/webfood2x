from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=True)  # 存储图片的二进制数据
    image_mimetype = db.Column(db.String(50), nullable=True)  # 存储图片类型 (MIME Type)

    def __init__(self, name, image_data=None, image_mimetype=None):
        self.name = name
        self.image_data = image_data
        self.image_mimetype = image_mimetype
