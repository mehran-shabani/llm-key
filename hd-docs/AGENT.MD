# Agent Instructions

This project includes a complete LLM-based application implemented in JavaScript. The goal is to **review all files and folders in the repository** and generate **technical documentation based strictly on the actual codebase**, not existing project documentation.

## Documentation Workflow

1. **Review All Source Folders and Files**:
   - Analyze each file independently.
   - Extract implementation details directly from code: logic, technologies, dependencies, patterns.
   - Categorize reviewed content into one of: `backend`, `frontend`, or `others`.

2. **Generate Markdown Files in `hd-docs/`**:
   - Create the following subdirectories inside `hd-docs/`:
     - `backend/`
     - `frontend/`
     - `others/`
   - For each reviewed module, generate a `.md` file inside the appropriate directory. Each file must include:
     - Purpose and role of the component
     - Key technologies and frameworks used (e.g., Express, Prisma, WebSocket)
     - Architecture or design patterns (e.g., MVC, layered, event-driven)
     - Code snippets with commentary (when relevant)
     - Important technical decisions or implementation details

3. **High-Level Project Overview**:
   - In the root of `hd-docs/`, create one or more `.md` files (e.g., `overview.md`, `system-architecture.md`) covering:
     - General architecture of the app
     - High-level data flow and component interaction
     - Role of the frontend, backend, and auxiliary components

4. **Critical Notes**:
   - Do **not** rely on any existing documentation files inside the repo.
   - All insights must be derived **directly from the code**.
   - Focus on **how** things are implemented, not just what they do.
