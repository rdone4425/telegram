import sqlite3
import requests
import os
import time
import logging
from datetime import datetime, timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)

# 设置Telegram Bot Token
BOT_TOKEN = '7468795202:AAEZ1ewWpHG8cj0pQTWyLdzVkwTtV1704fA'  # 请在这里填写您的Telegram Bot Token

# 获取数据库连接
def get_db_connection():
    return sqlite3.connect('employee.db')

# 创建数据库连接
def create_database():
    with get_db_connection() as conn:
        if not conn:
            return
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS employee
                     (date TEXT PRIMARY KEY, hours REAL, hourly_rate REAL, is_rest INTEGER)''')
        conn.commit()

def check_existing_record(date):
    with get_db_connection() as conn:
        if not conn:
            return False
        c = conn.cursor()
        c.execute("SELECT * FROM employee WHERE date = ?", (date,))
        existing_record = c.fetchone()
    return existing_record is not None

def get_last_recorded_date():
    with get_db_connection() as conn:
        if not conn:
            return None
        c = conn.cursor()
        c.execute("SELECT date FROM employee ORDER BY date DESC LIMIT 1")
        last_date = c.fetchone()
    return last_date[0] if last_date else None

def save_or_update_data(date, hours):
    hourly_rate = 22.0  # 请在这里填写每小时的工资率
    is_rest = 1 if hours == 0 else 0
    with get_db_connection() as conn:
        if not conn:
            return
        c = conn.cursor()
        if check_existing_record(date):
            c.execute("UPDATE employee SET hours = ?, hourly_rate = ?, is_rest = ? WHERE date = ?", (hours, hourly_rate, is_rest, date))
        else:
            c.execute("INSERT INTO employee (date, hours, hourly_rate, is_rest) VALUES (?, ?, ?, ?)", (date, hours, hourly_rate, is_rest))
        conn.commit()

def send_message(chat_id, text):
    url = f"https://tg.910626.xyz/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"发送消息失败: {e}")
        return None

def handle_message(message):
    chat_id = message['chat']['id']
    user_input = message['text'].split()
    if len(user_input) != 1:
        send_message(chat_id, '输入格式不正确，请输入工时')
        return

    try:
        hours = float(user_input[0])
        if hours < 0:
            raise ValueError("工时不能为负数")
    except ValueError as e:
        send_message(chat_id, f'工时输入错误: {e}')
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    last_recorded_date = get_last_recorded_date()

    if last_recorded_date:
        last_recorded_date = datetime.strptime(last_recorded_date, "%Y-%m-%d")
        missing_dates = []
        while last_recorded_date < datetime.now():
            last_recorded_date += timedelta(days=1)
            missing_date_str = last_recorded_date.strftime("%Y-%m-%d")
            if missing_date_str < current_date and not check_existing_record(missing_date_str):
                missing_dates.append(missing_date_str)

        if missing_dates:
            send_message(chat_id, f'您有以下日期忘记记录工时：{", ".join(missing_dates)}。请先补录这些日期的工时。')
            return

    save_or_update_data(current_date, hours)
    send_message(chat_id, f'已记录日期 {current_date} 的工时为 {hours}')

def get_updates(offset=None):
    url = f"https://tg.910626.xyz/bot{BOT_TOKEN}/getUpdates"
    params = {"offset": offset} if offset else {}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"获取更新失败: {e}")
        return {"ok": False, "result": []}

def get_summary(start_date, end_date):
    with get_db_connection() as conn:
        if not conn:
            return 0, 0
        c = conn.cursor()
        c.execute("SELECT date, hours, hourly_rate FROM employee WHERE date >= ? AND date <= ?", (start_date, end_date))
        records = c.fetchall()

    total_hours = sum(record[1] for record in records)
    total_salary = sum(record[1] * record[2] for record in records)
    return total_hours, total_salary

def get_weekly_summary():
    current_date = datetime.now()
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    start_date = start_of_week.strftime("%Y-%m-%d")
    end_date = end_of_week.strftime("%Y-%m-%d")

    total_hours, total_salary = get_summary(start_date, end_date)
    return f'本周工时总结：总工时 {total_hours} 小时，总薪资 {total_salary:.2f} 元'

def get_monthly_summary():
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    if start_of_month.month == 12:
        end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = start_of_month.replace(month=start_of_month.month + 1, day=1) - timedelta(days=1)

    start_date = start_of_month.strftime("%Y-%m-%d")
    end_date = end_of_month.strftime("%Y-%m-%d")

    total_hours, total_salary = get_summary(start_date, end_date)
    return f'本月工时总结：总工时 {total_hours} 小时，总薪资 {total_salary:.2f} 元'

def handle_command(message):
    chat_id = message['chat']['id']
    command = message['text']

    if command == '/本周':
        summary = get_weekly_summary()
        send_message(chat_id, summary)
    elif command == '/本月':
        summary = get_monthly_summary()
        send_message(chat_id, summary)
    else:
        send_message(chat_id, "未知命令，请输入 /本周 或 /本月")

def main():
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            if updates['ok']:
                for update in updates['result']:
                    if 'message' in update and 'text' in update['message']:
                        if update['message']['text'].startswith('/'):
                            handle_command(update['message'])
                        else:
                            handle_message(update['message'])
                    offset = update['update_id'] + 1
            time.sleep(1)  # 添加延迟以避免频繁请求
        except Exception as e:
            logging.error(f"主循环中出现错误: {e}")
            time.sleep(5)  # 出错时等待更长时间

if __name__ == "__main__":
    create_database()
    if not BOT_TOKEN:
        logging.error("未设置 Telegram bot token")
        exit(1)
    main()
