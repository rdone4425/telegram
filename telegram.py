import sqlite3
import requests
from datetime import datetime, timedelta
import logging

# 全局变量
TOKEN = '7468795202:AAEZ1ewWpHG8cj0pQTWyLdzVkwTtV1704fA'  # 替换为你的Telegram Bot Token
HOURLY_RATE = 22.0  # 默认时薪

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 月份名称转换为中文
MONTH_NAMES = {
    1: '一月', 2: '二月', 3: '三月', 4: '四月', 5: '五月', 6: '六月',
    7: '七月', 8: '八月', 9: '九月', 10: '十月', 11: '十一月', 12: '十二月'
}

# 创建数据库连接
def create_database():
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS employee
                 (date TEXT PRIMARY KEY, hours REAL, hourly_rate REAL, is_rest INTEGER)''')
    conn.commit()
    conn.close()

# 检查当天是否已有记录
def check_existing_record(date):
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute("SELECT * FROM employee WHERE date = ?", (date,))
    existing_record = c.fetchone()
    conn.close()
    return existing_record is not None

# 获取最近一次记录的日期
def get_last_recorded_date():
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute("SELECT date FROM employee ORDER BY date DESC LIMIT 1")
    last_date = c.fetchone()
    conn.close()
    return last_date[0] if last_date else None

# 保存或更新数据到数据库
def save_or_update_data(date, hours):
    is_rest = 1 if hours == 0 else 0  # 如果工时为0，标记为休息日
    conn = sqlite3.connect('employee.db')
    c = conn.cursor()

    if check_existing_record(date):
        c.execute("UPDATE employee SET hours = ?, hourly_rate = ?, is_rest = ? WHERE date = ?", (hours, HOURLY_RATE, is_rest, date))
    else:
        c.execute("INSERT INTO employee (date, hours, hourly_rate, is_rest) VALUES (?, ?, ?, ?)", (date, hours, HOURLY_RATE, is_rest))

    conn.commit()
    conn.close()

# 发送消息到Telegram
def send_message(chat_id, text):
    url = f"https://tg.910626.xyz/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # 检查请求是否成功
        return response.json()
    except requests.RequestException as e:
        logger.error(f"发送消息失败: {e}")
        return None

# 处理Telegram消息
def handle_message(message):
    chat_id = message['chat']['id']
    user_input = message['text'].split()
    if len(user_input) == 1:
        handle_daily_record(chat_id, user_input[0])
    elif len(user_input) == 2:
        handle_backlog_record(chat_id, user_input[0], user_input[1])
    else:
        send_message(chat_id, '输入格式不正确，请输入工时或日期和工时')

# 处理每日记录
def handle_daily_record(chat_id, hours_str):
    try:
        hours = float(hours_str)
        if hours < 0:
            raise ValueError("工时不能为负数")
    except ValueError as e:
        send_message(chat_id, f'工时必须是数字且不能为负数: {e}')
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    save_or_update_data(current_date, hours)
    send_message(chat_id, f'已记录日期 {current_date} 的工时为 {hours}')

# 处理补录记录
def handle_backlog_record(chat_id, date_str, hours_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        send_message(chat_id, '日期格式不正确，请使用 YYYY-MM-DD 格式')
        return

    try:
        hours = float(hours_str)
        if hours < 0:
            raise ValueError("工时不能为负数")
    except ValueError:
        send_message(chat_id, '工时必须是数字且不能为负数')
        return

    save_or_update_data(date_str, hours)
    send_message(chat_id, f'已补录日期 {date_str} 的工时为 {hours}')

# 获取Telegram更新
def get_updates(offset=None):
    url = f"https://tg.910626.xyz/bot{TOKEN}/getUpdates"
    params = {"offset": offset} if offset else {}
    response = requests.get(url, params=params)
    return response.json()

# 获取每周总结
def get_weekly_summary():
    # 获取当前日期所在的周的起始日期（周一）和结束日期（周日）
    current_date = datetime.now()
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    start_date = start_of_week.strftime("%Y-%m-%d")
    end_date = end_of_week.strftime("%Y-%m-%d")

    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute("SELECT date, hours, hourly_rate, is_rest FROM employee WHERE date >= ? AND date <= ?", (start_date, end_date))
    records = c.fetchall()
    conn.close()

    total_hours = sum(record[1] for record in records)
    total_salary = sum(record[1] * record[2] for record in records)
    rest_days = sum(1 for record in records if record[3] == 1)
    work_days = len(records) - rest_days
    return f'本周工时总结：总工时 {total_hours} 小时，总薪资 {total_salary} 元，工作天数 {work_days} 天，休息天数 {rest_days} 天'

# 获取每月总结
def get_monthly_summary():
    # 获取当前日期所在的月的起始日期（1号）和结束日期（当月最后一天）
    current_date = datetime.now()
    start_of_month = current_date.replace(day=1)
    if start_of_month.month == 12:
        end_of_month = start_of_month.replace(year=start_of_month.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = start_of_month.replace(month=start_of_month.month + 1, day=1) - timedelta(days=1)

    start_date = start_of_month.strftime("%Y-%m-%d")
    end_date = end_of_month.strftime("%Y-%m-%d")

    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute("SELECT date, hours, hourly_rate, is_rest FROM employee WHERE date >= ? AND date <= ?", (start_date, end_date))
    records = c.fetchall()
    conn.close()

    total_hours = sum(record[1] for record in records)
    total_salary = sum(record[1] * record[2] for record in records)
    rest_days = sum(1 for record in records if record[3] == 1)
    work_days = len(records) - rest_days
    return f'本月工时总结：总工时 {total_hours} 小时，总薪资 {total_salary} 元，工作天数 {work_days} 天，休息天数 {rest_days} 天'

# 获取上月总结
def get_last_month_summary():
    # 获取上个月的起始日期（1号）和结束日期（当月最后一天）
    current_date = datetime.now()
    if current_date.month == 1:
        start_of_last_month = current_date.replace(year=current_date.year - 1, month=12, day=1)
        end_of_last_month = start_of_last_month.replace(month=1, day=1) - timedelta(days=1)
    else:
        start_of_last_month = current_date.replace(month=current_date.month - 1, day=1)
        end_of_last_month = start_of_last_month.replace(month=start_of_last_month.month + 1, day=1) - timedelta(days=1)

    start_date = start_of_last_month.strftime("%Y-%m-%d")
    end_date = end_of_last_month.strftime("%Y-%m-%d")
    month_name = MONTH_NAMES[start_of_last_month.month]  # 获取上个月的月份名称

    conn = sqlite3.connect('employee.db')
    c = conn.cursor()
    c.execute("SELECT date, hours, hourly_rate, is_rest FROM employee WHERE date >= ? AND date <= ?", (start_date, end_date))
    records = c.fetchall()
    conn.close()

    total_hours = sum(record[1] for record in records)
    total_salary = sum(record[1] * record[2] for record in records)
    rest_days = sum(1 for record in records if record[3] == 1)
    work_days = len(records) - rest_days
    return f'{month_name} 工时总结：总工时 {total_hours} 小时，总薪资 {total_salary} 元，工作天数 {work_days} 天，休息天数 {rest_days} 天'

# 处理命令
def handle_command(message):
    chat_id = message['chat']['id']
    command = message['text']

    if command == '/本周':
        summary = get_weekly_summary()
        send_message(chat_id, summary)
    elif command == '/本月':
        summary = get_monthly_summary()
        send_message(chat_id, summary)
    elif command == '/上月':
        summary = get_last_month_summary()
        send_message(chat_id, summary)
    elif command == '/帮助':
        help_text = "可用命令:\n/本周 - 获取本周工时总结\n/本月 - 获取本月工时总结\n/上月 - 获取上月工时总结\n/帮助 - 显示帮助信息\n直接输入工时或日期和工时进行记录或补录"
        send_message(chat_id, help_text)

# 主函数
def main():
    if not TOKEN:
        raise ValueError("请设置Telegram Bot Token")
    
    offset = None
    while True:
        updates = get_updates(offset)
        if updates['ok']:
            for update in updates['result']:
                if 'text' in update['message']:
                    if update['message']['text'].startswith('/'):
                        handle_command(update['message'])
                    else:
                        handle_message(update['message'])
                offset = update['update_id'] + 1

if __name__ == "__main__":
    create_database()
    main()
