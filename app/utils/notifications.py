import json
from datetime import datetime

import app
from app.keyboards.inline.course_keyboard import get_course_keyboard
from app.utils.api import read_notification
from app.utils.staff import solution_result


async def send_notifications(user_id, notifications_json, cookies, csrf_token):
    notifications: dict = notifications_json["notificationMap"]
    for notification in notifications.values():
        text = "<b>🔔 Новое уведомление </b> \n\n"
        notification_type = notification["type"]

        await read_notification(cookies, notification['id'], csrf_token)

        reply_markup = None

        if notification_type == "lesson-opened":
            text += f"📚 Открыт новый урок <b>{notification['objectData']['title']}</b> \n"
            date = datetime.fromisoformat(notification['addedTime'])
            text += f"📅 Дата и время: <b>{date.strftime('%d.%m.%Y %H:%M')}</b> \n"
            course_id = notification["objectData"]["course"]
            lesson_id = notification["objectData"]["lessonId"]
            group_id = notification["objectData"]["group"]
            reply_markup = get_course_keyboard(course_id, group_id, lesson_id)
        elif notification_type == "bonus-score-changed":
            text += f"📈 {notification['objectData']['changedBy']} изменил(а) ваш бонусный балл с {notification['objectData']['oldScore']} на {notification['objectData']['newScore']} \n"
        elif notification_type == "task-solution-reviewed":
            text += f"📊 Статус задачи {notification['objectData']['task']['title']} урока {notification['objectData']['task']['lesson']['title']} изменился на {solution_result[notification['objectData']['status']['type']]} \n"
        elif notification_type == "task-solution-commented":
            text += f"✍️ {notification['objectData']['author']['displayName']} оставил(а) комментарий к задаче {notification['objectData']['taskSolution']['task']['title']} урока {notification['objectData']['taskSolution']['task']['lesson']['title']}:" \
                    f"<code>{notification['objectData']['data']}</code> \n"
        elif notification_type == "submission-checked":
            text += f"📊 Статус задачи <b>{notification['objectData']['taskSolution']['task']['title']}</b> урока <b>{notification['objectData']['taskSolution']['task']['lesson']['title']}</b> изменился на <b>{solution_result[notification['objectData']['taskSolution']['status']['type']]}</b> \n"

        await app.bot.send_message(user_id, text, reply_markup=reply_markup)

