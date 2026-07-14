# CLAUDE.md

# AI Software QA Deep Agent

## Project Overview

This repository contains an AI-powered Software QA Engineer built using **LangChain Deep Agents**.

The system validates software changes before deployment.

The agent acts as a senior QA engineer responsible for:

- Understanding implemented features
- Analyzing code changes
- Verifying test coverage
- Executing existing tests
- Analyzing failures
- Updating documentation
- Generating QA reports
- Making deployment recommendations

The agent DOES NOT:

- Modify application source code
- Generate tests
- Fix bugs automatically

This is version 0.

The goal is to create a reliable QA validation pipeline.

---

# Core Architecture Principle

This project follows an:

## AI Reasoning + Deterministic Tools Architecture

The LLM should only perform tasks requiring reasoning.

Examples:

- Understanding git changes
- Explaining test failures
- Generating documentation
- Summarizing QA results

The LLM should NOT perform deterministic operations.

Examples:

- Running tests
- Parsing coverage reports
- Reading files
- Executing commands
- Calculating metrics

Those responsibilities belong to Python tools.

---

# High-Level Architecture

```
                    Deep QA Agent

                          |
                          |

                 Tool Selection Layer

                          |

 -------------------------------------------------

 |              |              |              |

Git Tool   Coverage Tool   Testing Tool   Documentation Tool

 |              |              |              |

Diff       Coverage       pytest         Markdown

Analysis   Analysis      Playwright      Updates

                         Locust

                          |

                          |

                    QA Report Tool
```

---

# Tech Stack

## Language

Python 3.12+

## AI Framework

- LangChain
- LangGraph
- LangChain Deep Agents

## Backend

- FastAPI

## Validation

- Pydantic

## Testing

- pytest
- Playwright
- Locust

## Utilities

- GitPython
- Docker
- Markdown

---

# Project Structure

```
qa-agent/

├── app/
│
│   ├── agent/
│   │   ├── deep_agent.py
│   │   ├── prompts.py
│   │   └── configuration.py
│   │
│   ├── tools/
│   │   ├── git_tools.py
│   │   ├── coverage_tools.py
│   │   ├── test_tools.py
│   │   ├── documentation_tools.py
│   │   ├── reporting_tools.py
│   │   └── deployment_tools.py
│   │
│   ├── models/
│   │   ├── state.py
│   │   ├── reports.py
│   │   └── schemas.py
│   │
│   ├── services/
│   │
│   ├── api/
│   │   └── routes.py
│   │
│   ├── utils/
│   │
│   └── main.py
│
├── tests/
│
├── docs/
│
├── prompts/
│
├── Dockerfile
│
└── README.md
```

---

# Deep Agent Responsibilities

The Deep Agent is the orchestrator.

It decides:

- Which tools to call
- Execution order
- Whether additional analysis is needed
- Whether deployment can continue

The Deep Agent should NOT contain business logic.

Business logic belongs inside tools.

---

# Available Tools

## Git Analysis Tool

### Purpose

Understand what changed in the repository.

### Responsibilities

- Inspect git diff
- List modified files
- Identify changed modules
- Identify affected APIs
- Identify affected frontend components

Example output:

```
Feature:

Task Editing

Modified Files:

backend/tasks/service.py
frontend/pages/tasks.py

Affected Area:

Task Management
```

---

# Coverage Analysis Tool

## Purpose

Verify that the implemented feature has appropriate testing coverage.

The tool does NOT generate tests.

It only analyzes existing coverage.

Checks:

- Unit tests
- Integration tests
- End-to-end tests
- Performance tests

Example output:

```
Coverage Report

Unit Tests:
PASS

Integration Tests:
PASS

E2E Tests:
MISSING

Performance Tests:
NOT REQUIRED
```

---

# Test Execution Tools

Responsible for running:

## Unit Tests

pytest

## Integration Tests

pytest integration suite

## End-to-End Tests

Playwright

## Performance Tests

Locust

The Deep Agent must never manually execute commands.

It must call tools.

---

# Test Result Parser

The system should parse:

- pytest reports
- Playwright reports
- Locust results

Do not send complete raw logs to the LLM unless necessary.

Extract:

- Passed tests
- Failed tests
- Execution time
- Error messages
- Coverage information

---

# Failure Analysis Tool

This tool runs only when tests fail.

Responsibilities:

Explain:

- Which tests failed
- Why they failed
- Possible root cause
- Affected component
- Severity

Example:

```
Failure:

test_update_task_status


Expected:

HTTP 422


Received:

HTTP 500


Possible Cause:

Missing validation inside task update service.
```

The tool must never modify source code.

---

# Documentation Tool

This tool runs ONLY after successful validation.

Updates:

- README
- API documentation
- Architecture documentation
- Changelog
- Release notes
- Testing documentation

Documentation must always represent the current implementation.

---

# QA Report Tool

Always generate a final QA report.

Example:

```
QA Report

Feature:

Task Editing


Tests:

Unit Tests:
32 Passed

Integration Tests:
8 Passed

E2E Tests:
6 Passed

Performance:
Passed


Documentation:

Updated


Deployment:

READY
```

Failure example:

```
QA Report

Deployment:

BLOCKED


Reason:

Tests failed.
```

---

# Workflow

The expected workflow:

```
START

↓

Receive feature validation request

↓

Analyze Git Changes

↓

Analyze Test Coverage

↓

Execute Tests

↓

Decision

        |
        |
        +----------------+
        |                |
     SUCCESS          FAILURE
        |                |
        |                |
Update Documentation  Analyze Failures
        |                |
        |                |
        +----------------+
                 |
                 |
            Generate QA Report
                 |
                 |
                END
```

---

# API Endpoints

## Health Check

```
GET /health
```

---

## Analyze Feature

```
POST /analyze
```

---

## Run QA Pipeline

```
POST /run
```

---

## Retrieve Reports

```
GET /reports
```

```
GET /reports/{id}
```

---

# State Management

Use Pydantic models.

The workflow state should contain:

```python
FeatureSummary

ChangedFiles

CoverageReport

TestResults

FailureAnalysis

DocumentationStatus

QAReport

DeploymentDecision
```

Avoid unstructured dictionaries.

---

# Coding Rules

Always:

- Use type hints
- Use Pydantic models
- Keep tools independent
- Write small functions
- Separate AI logic from execution logic
- Keep prompts isolated

Avoid:

- Giant agent files
- Hidden state
- Unnecessary LLM calls
- Duplicated logic

---

# Prompt Engineering Rules

Prompts must:

- Live in separate files
- Be version controlled
- Have clear objectives
- Define expected outputs

Avoid:

- Asking the LLM to perform deterministic tasks
- Large vague prompts
- Mixing multiple responsibilities

---

# Error Handling

A failure in one tool should not crash the entire workflow.

Return structured errors.

Example:

```json
{
  "status": "failed",
  "tool": "pytest_runner",
  "error": "pytest execution timeout"
}
```

---

# Logging

Log:

- Agent execution
- Tool execution
- Execution time
- Errors

Never log:

- API keys
- Passwords
- Tokens
- Sensitive information

---

# Testing Requirements

The QA Agent itself must contain tests.

## Unit Tests

Test:

- Tools
- Parsers
- Models
- Utilities

## Integration Tests

Test:

- Agent workflow
- API endpoints
- Tool execution pipeline

Mock:

- LLM calls
- External services

---

# Future Extensions

The architecture should allow adding:

## Test Generation Agent

Automatically creates missing tests.

## Security Agent

Analyzes vulnerabilities.

## Dependency Agent

Checks outdated dependencies.

## Code Review Agent

Reviews pull requests.

## Performance Optimization Agent

Analyzes bottlenecks.

---

# Final Goal

Build a realistic autonomous QA engineer.

The system should demonstrate:

- Deep Agent orchestration
- Tool-based AI architecture
- Automated software validation
- Automated documentation
- Deployment readiness decisions

The principle of the system is:

**The LLM should reason.  
Python should execute.**