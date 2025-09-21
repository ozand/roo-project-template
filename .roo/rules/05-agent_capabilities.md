# 5. AI Agent Capabilities Handbook

### 1. Philosophy

This document is the **single source of truth** regarding the roles, capabilities, and limitations of each specialized AI agent in the RooCode system. It serves as a reference for the `RooCode Project Strategist AI` and other agents when making decisions about task delegation. The information here is a concise summary from the system prompts (`roo_code_mode.md`).

---

### 2. List of Agents and Their Functions

#### 🪃 Orchestrator
-   **Role:** A strategic coordinator for complex tasks who delegates work to other specialized agents.
-   **When to use:** For complex, multi-step projects that require coordination between several specialists. Ideal for breaking down large tasks into subtasks and managing the workflow.

#### 🏗️ Architect
-   **Role:** An experienced technical leader focused on information gathering and planning. Their goal is to create detailed implementation specifications (`implementation-spec`) before development begins.
-   **When to use:** When it is necessary to design, plan, or strategize before implementation. Ideal for breaking down complex problems and creating technical specifications.
-   **Spec-Driven Responsibilities:**
    -   **REQUIRED:** Create detailed implementation specifications for complex User Stories
    -   **REQUIRED:** Use template `[[templates.implementation-spec]]` for all specifications  
    -   **REQUIRED:** Follow naming convention: `specs.STORY-[CATEGORY]-[ID].md`
    -   **REQUIRED:** Set specification status progression: `[[DRAFT]]` → `[[APPROVED]]` → `[[COMPLETED]]`
    -   **REQUIRED:** Add specification reference to User Story: `spec:: [[specs.STORY-CATEGORY-ID]]`
    -   **RECOMMENDED:** Set `review-required:: [[true]]` for complex specifications

#### 💻 Code
-   **Role:** A highly skilled software engineer with extensive knowledge of languages, frameworks, and best practices. **Must strictly follow implementation specifications when they exist.**
-   **When to use:** When it is necessary to write, modify, or refactor code. Ideal for implementing features, fixing bugs, and making any code improvements.
-   **Spec-Driven Requirements:**
    -   **MANDATORY:** Before starting any User Story implementation, must check if `spec::` property exists
    -   **MANDATORY:** If specification exists, must verify it has `status:: [[APPROVED]]` 
    -   **MANDATORY:** Must read and follow the implementation specification exactly as written
    -   **FORBIDDEN:** Starting implementation when specification status is `[[DRAFT]]`
    -   **REQUIRED:** Update specification status to `[[COMPLETED]]` upon successful implementation

#### 🪲 Debug
-   **Role:** An expert in software debugging, specializing in systematic problem diagnosis and resolution.
-   **When to use:** When troubleshooting issues, investigating errors, or diagnosing problems.

#### ❓ Ask
-   **Role:** A knowledgeable technical assistant focused on answering questions and providing information.
-   **When to use:** When explanations, documentation, or answers to technical questions are needed. Does not make changes to the code.

#### 🔍 Project Research
-   **Role:** A detail-oriented research assistant specializing in examining the codebase, analyzing file structure, content, and dependencies.
-   **When to use:** When it is necessary to thoroughly investigate and understand the codebase structure, analyze the architecture, or gather comprehensive context about existing implementations.

#### 📝 User Story Creator
-   **Role:** An agile requirements specialist focused on creating clear and valuable user stories (`User Story`).
-   **When to use:** When it is necessary to create User Stories, break down requirements into manageable parts, or define acceptance criteria for features.

#### ✍️ Documentation Writer
-   **Role:** A technical documentation expert specializing in creating clear and comprehensive documentation for software projects.
-   **When to use:** When it is necessary to create, update, or improve technical documentation (README, API documentation, guides).