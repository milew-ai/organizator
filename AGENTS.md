# AGENTS.md - AI Coding Agent Guidelines

Welcome to **Organizator**. This document defines the engineering standards, architectural conventions, and operational workflows for AI agents working in this repository. 

For general project information, see [README.md](README.md).

---

## 1. Project Overview
- **Repository:** Organizator
- **Objective:** Modular utility workspace for organization and task management.
- **Tech Stack:** To be specified upon feature implementation.

---

## 2. Core Engineering Principles
- **Simplicity & Maintainability:** Write clean, readable, and self-documenting code. Prefer explicit composition over complex inheritance.
- **Type Safety:** Adhere strictly to language type systems and avoid unjustified type casting, suppression flags, or hacks.
- **Robust Error Handling:** Handle errors explicitly with informative context. Avoid silent failures or unhandled rejections.
- **Modularity:** Keep functions, classes, and modules small and focused on a single responsibility.

---

## 3. Development Lifecycle
1. **Research:** Systematically inspect existing code structures, dependencies, and patterns before proposing or implementing changes.
2. **Strategy:** Formulate a concise, robust plan aligned with the user's intent.
3. **Execution:** Apply surgical, targeted code modifications.
4. **Validation:** Run all relevant tests, linters, and type checks to guarantee behavioral and structural correctness.

---

## 4. Git & Contribution Standards
- **Commit Messages:** Clear, concise, and written in the imperative mood (e.g., `Add task categorization module`, `Fix invalid date parsing`).
- **Scope Discipline:** Only modify files and modules directly relevant to the current task. Avoid unsolicited refactoring or formatting changes.
