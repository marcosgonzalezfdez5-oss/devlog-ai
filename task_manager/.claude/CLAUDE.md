# CLAUDE.md

# Task Manager

## Project Overview

This repository contains a simple Task Manager application whose primary purpose is to act as the **System Under Test (SUT)** for the AI Software QA Agent.

This application is intentionally simple. New features should only be added if they improve testing scenarios.

The application is NOT intended to become a production SaaS.

---

# Tech Stack

Frontend
- Streamlit

Backend
- FastAPI

Database
- Supabase PostgreSQL

Authentication
- Supabase Auth

Testing
- pytest
- Playwright
- Locust

Python Version

3.12+

---

# Architecture

Frontend

Streamlit

↓

FastAPI

↓

Service Layer

↓

Repository Layer

↓

Supabase

The frontend must NEVER access the database directly.

All communication must go through the FastAPI backend.

---

# Application Features

The application only contains:

- Login
- Dashboard
- View Tasks
- Create Task
- Edit Task
- Delete Task
- Update Task Status

No additional modules should be introduced unless explicitly requested.

---

# Task Model

A task contains:

- title
- description
- priority
- status
- assigned_to
- created_at
- updated_at

Status flow:

Pending

↓

In Progress

↓

Review

↓

Completed

---

# Backend Structure

backend/

app/

api/

services/

repositories/

models/

schemas/

utils/

main.py

---

# Frontend Structure

frontend/

app.py

-pages/

-components/

-services/

---

# Development Principles

Always separate:

API

↓

Business Logic

↓

Database Access

Business logic should never be implemented inside API endpoints.

---

# API Guidelines

Use REST conventions.

Examples:

GET /tasks

POST /tasks

PUT /tasks/{id}

DELETE /tasks/{id}

PATCH /tasks/{id}/status

GET /dashboard

---

# Error Handling

Always return proper HTTP status codes.

400

Bad Request

401

Unauthorized

403

Forbidden

404

Not Found

422

Validation Error

500

Internal Error

---

# Testing Requirements

Every new feature MUST include:

Unit tests

Integration tests

Playwright E2E tests (when UI changes)

Performance tests if the feature introduces expensive operations.

Tests are mandatory.

---

# Documentation

Every API endpoint should include:

- Description
- Request model
- Response model
- Status codes

Use FastAPI automatic OpenAPI generation whenever possible.

---

# Code Style

- Type hints required.
- Small functions.
- Single responsibility.
- Avoid duplicated code.
- Use dependency injection where appropriate.
- Prefer composition over inheritance.

---

# Database

Supabase is the single source of truth.

Never write raw SQL unless absolutely necessary.

Use repository classes for database interactions.

---

# Logging

Log:

- API requests
- Errors
- Exceptions

Do not log passwords or secrets.

---

# Security

Validate every request.

Never trust frontend input.

Sanitize all incoming data.

Use Pydantic validation.

---

# Goal

This application exists to be tested.

Prioritize maintainability, readability, and realistic software architecture over adding unnecessary features.