max = {
    "classwork": 10,
    "homework": 10,
    "additional": 40,
    "control-work": 40,
    "individual-work": 20,
}

k_lessons = {
    "classwork": 40,
    "homework": 40,
    "additional": 45,
    "control-work": 2,
}


def calculate_score(primary_score, task_type, second_year):
    if task_type == "individual-work":
        if second_year:
            return primary_score / 100 * max[task_type] / 3
        else:
            return primary_score / 100 * max[task_type] / 4
    return round(primary_score / 100 * max[task_type] / k_lessons[task_type], 2)
