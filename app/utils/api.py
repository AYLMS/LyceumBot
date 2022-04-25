import pickle

from aiohttp import ClientSession


async def get_user_information(
    with_courses_summary: bool,
    with_expelled: bool,
    with_children: bool,
    with_parents: bool,
    cookies: bytes,
):
    cookies = pickle.loads(cookies)
    session = ClientSession(cookies=cookies)
    return await (
        await session.get(
            "https://lyceum.yandex.ru/api/profile",
            params={
                "withCoursesSummary": str(with_courses_summary).lower(),
                "withExpelled": str(with_expelled).lower(),
                "withChildren": str(with_children).lower(),
                "withParents": str(with_parents).lower(),
            },
        )
    ).json()


async def get_solution_information(solution_id, cookies):
    cookies = pickle.loads(cookies)
    session = ClientSession(cookies=cookies)
    return await (
        await session.get(
            f"https://lyceum.yandex.ru/api/student/solutions/{solution_id}"
        )
    ).json()
