"""Disco.co LMS tool (Manual 29.4). Mock by default ($0, no key).

CrediVersity micro-credential LMS. Used by hermes-crediversity for course
management and enrollment. Live mode needs ``DISCO_API_KEY``.
"""

import os

from tools import is_live

DISCO_BASE = "https://api.disco.co/v1"


async def get_courses() -> dict:
    if is_live("DISCO_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{DISCO_BASE}/courses",
                headers={"Authorization": f"Bearer {os.environ['DISCO_API_KEY']}"},
            )
            return {"courses": r.json().get("data", [])}

    courses = [
        {"id": "crs_ai101", "title": "AI Tools for Canadian Students", "enrolled": 142},
        {"id": "crs_resume", "title": "ATS-Proof Resume Micro-Credential", "enrolled": 88},
        {"id": "crs_sidehustle", "title": "The AI Side Hustle Blueprint", "enrolled": 211},
    ]
    return {"mock": True, "courses": courses, "count": len(courses)}


async def get_enrollments(course_id: str) -> dict:
    if is_live("DISCO_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{DISCO_BASE}/courses/{course_id}/enrollments",
                headers={"Authorization": f"Bearer {os.environ['DISCO_API_KEY']}"},
            )
            return {"enrollments": r.json().get("data", [])}

    enrollments = [
        {"email": "sarah.c@uoft.ca", "status": "in_progress", "progress": 0.62},
        {"email": "j.okafor@yorku.ca", "status": "completed", "progress": 1.0},
    ]
    return {"mock": True, "course_id": course_id, "enrollments": enrollments, "count": len(enrollments)}


async def enroll_learner(course_id: str, email: str) -> dict:
    if is_live("DISCO_API_KEY"):  # pragma: no cover - needs key
        import httpx

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{DISCO_BASE}/courses/{course_id}/enrollments",
                headers={"Authorization": f"Bearer {os.environ['DISCO_API_KEY']}"},
                json={"email": email},
            )
            return r.json()

    return {"mock": True, "status": "enrolled", "course_id": course_id, "email": email,
            "enrollment_id": f"mock_enr_{abs(hash(course_id + email)) % 100000}"}
