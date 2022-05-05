from datetime import datetime

from app.keyboards.inline.course_keyboard import get_course_keyboard, \
    get_task_keyboard
from app.utils.api import read_notification


async def send_notifications(notifications_json, cookies, csrf_token):
    notifications: dict = notifications_json["notificationMap"]

    await read_notification(cookies, csrf_token)

    notis = []
    for notification in notifications.values():
        text = "<b>🔔 Новое уведомление </b> \n\n"
        notification_type = notification["type"]

        reply_markup = None

        if notification_type == "lesson-opened":
            text += (
                f"📚 Открыт новый урок <b>{notification['objectData']['title']}</b> \n"
            )
            date = datetime.fromisoformat(notification["addedTime"])
            text += f"📅 Дата и время: <b>{date.strftime('%d.%m.%Y %H:%M')}</b> \n"
            course_id = notification["objectData"]["course"]
            lesson_id = notification["objectData"]["lessonId"]
            group_id = notification["objectData"]["group"]
            reply_markup = get_course_keyboard(course_id, group_id, lesson_id)

        elif notification_type == "bonus-score-changed":
            text += f"📈 <b>{notification['objectData']['changedBy']}</b> изменил(а) ваш бонусный балл \n" \
                    f" <code>C {notification['objectData']['oldScore']} на {notification['objectData']['newScore']} </code>\n"

        elif notification_type == "task-solution-reviewed":
            emoji = (
                "🟢"
                if notification["objectData"]["score"]
                   == notification["objectData"]["task"]["scoreMax"]
                else "🔴"
            )
            text += (
                f"{emoji} <i>Проверена задача</i> <b>{notification['objectData']['task']['title']}</b> <code>{notification['objectData']['score']} / {notification['objectData']['task']['scoreMax']} </code>\n"
                f"<b>Урок:</b> <code>{notification['objectData']['task']['lesson']['title']} </code>\n"
            )
            course_id = notification["objectData"]["task"]["course"]
            lesson_id = notification["objectData"]["task"]["lesson"]["id"]
            group_id = notification["objectData"]["task"]["group"]
            task_id = notification["objectData"]["task"]["id"]
            solution_id = notification["objectData"]["taskSolutionId"]
            reply_markup = get_task_keyboard(course_id, group_id, lesson_id,
                                             task_id, solution_id)

        elif notification_type == "task-solution-commented":
            text += (
                f"✍️ <b>{notification['objectData']['author']['displayName']}</b> оставил(а) комментарий \n"
                f"<b>Задача:</b> <code>{notification['objectData']['taskSolution']['task']['title']}</code> \n"
                f"<b>Урок:</b> <code>{notification['objectData']['taskSolution']['task']['lesson']['title']}</code> \n\n"
                f"<code>{notification['objectData']['data']}</code> \n"
            )

        elif notification_type == "submission-checked":
            emoji = (
                "🟢"
                if notification["objectData"]["taskSolution"]["score"]
                   == notification["objectData"]["taskSolution"]["task"]["scoreMax"]
                else "🔴"
            )
            text += (
                f"{emoji} <i>Проверена задача</i> <b>{notification['objectData']['taskSolution']['task']['title']}</b> <code>{notification['objectData']['taskSolution']['score']} / {notification['objectData']['taskSolution']['task']['scoreMax']}</code> \n"
                f"<b>Урок:</b> <code>{notification['objectData']['taskSolution']['task']['lesson']['title']} </code>\n"
            )
            course_id = notification["objectData"]['taskSolution']["task"]["course"]
            lesson_id = notification["objectData"]['taskSolution']["task"]["lesson"]["id"]
            group_id = notification["objectData"]['taskSolution']["task"]["group"]
            task_id = notification["objectData"]['taskSolution']["task"]["id"]
            solution_id = notification["objectData"]['taskSolution']["id"]
            reply_markup = get_task_keyboard(course_id, group_id, lesson_id,
                                             task_id, solution_id)
        notis.append((text, reply_markup))

    return notis
