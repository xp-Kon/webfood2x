import smtplib
from email.mime.text import MIMEText
from config import EMAIL, PASSWORD

def send_email(to_email, order_list):
    msg = MIMEText(f"您的订单：\n\n{order_list}")
    msg["Subject"] = "情侣点餐订单"
    msg["From"] = EMAIL
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.qq.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, to_email, msg.as_string())
