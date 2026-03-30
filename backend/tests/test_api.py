"""Tests for the API routes."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthCheck:
    def test_health_returns_ok(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestCrawlEndpoint:
    def test_start_crawl_valid(self):
        response = client.post("/api/crawl", json={
            "url": "https://example.com",
            "depth": 1,
            "same_domain_only": True,
        })
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"
        assert data["depth"] == 1

    def test_start_crawl_invalid_depth(self):
        response = client.post("/api/crawl", json={
            "url": "https://example.com",
            "depth": 10,
        })
        assert response.status_code == 422

    def test_start_crawl_invalid_url(self):
        response = client.post("/api/crawl", json={
            "url": "not-a-url",
            "depth": 1,
        })
        assert response.status_code == 422


class TestJobsEndpoint:
    def test_list_jobs(self):
        response = client.get("/api/jobs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_nonexistent_job(self):
        response = client.get("/api/jobs/nonexistent")
        assert response.status_code == 404
