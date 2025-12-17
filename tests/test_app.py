import os
import sys
import pytest

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app import app  # type: ignore
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_activities():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get("/activities")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert isinstance(data, dict)
    assert "Tennis Club" in data


@pytest.mark.asyncio
async def test_signup_new_participant():
    email = "pytest_user@example.com"
    activity = "Tennis Club"

    # ensure not already signed up
    async with AsyncClient(app=app, base_url="http://test") as ac:
        before = (await ac.get("/activities")).json()
        assert email not in before[activity]["participants"]

        # sign up
        resp = await ac.post(f"/activities/{activity}/signup", params={"email": email})
        assert resp.status_code == status.HTTP_200_OK

        # verify added
        after = (await ac.get("/activities")).json()
        assert email in after[activity]["participants"]


@pytest.mark.asyncio
async def test_signup_duplicate_fails():
    activity = "Tennis Club"
    existing = "james@mergington.edu"

    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(f"/activities/{activity}/signup", params={"email": existing})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
