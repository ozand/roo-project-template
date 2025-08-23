# 4\. Project Knowledge Base Management Standard

### 1\. Philosophy and Goals

This document is the **single and exhaustive source of truth** for organizing and maintaining the project's knowledge base. Its purpose is to ensure a strict, machine-readable, and consistent structure that solves two problems:

1. **For Logseq:** To create a cohesive, easily navigable, and queryable knowledge graph for humans.
2. **For AI agents:** To provide an unambiguous, algorithmic set of rules for creating, updating, and validating all project artifacts.

Deviation from these rules is not permitted.

-----

### 2\. Knowledge Repository Structure

#### 2.1. Graph Root

The root directory of the entire project (`b2bfinder/`) is the root of the Logseq graph. This allows for the creation of direct, clickable links from documentation to code and test files.

#### 2.2. Mandatory Structure and Purpose of Folders

AI agents are required to create new files only in the locations specified below.

* `pages/`: **The central repository for permanent knowledge.** Contains all primary, long-living, and structured project documents (requirements, User Stories, architectural decisions, rules, dashboards).
* `journals/`: **A chronological work log.** Used for daily, temporary notes, work logs, rough thoughts, and meeting minutes. Information from the journal should eventually be migrated and structured into `pages/`.
* `assets/`: For storing images and other media files embedded in documents.
* `logseq/`: A folder automatically managed by Logseq. AI agents are forbidden from modifying this folder directly.

-----

### 3\. Protocol for Creating and Naming Files in `pages/`

To logically group documents, a **namespace** mechanism is used, which is implemented via a `.` in the filename.

* **User Stories:**

  * **Location:** `pages/`
  * **Filename Format:** `STORY-[CATEGORY]-[ID].md` (e.g., `STORY-API-1.md`)
  * **Logseq Page Name:** `[[STORY-API-1]]`

* **Requirements:**

  * **Location:** `pages/`
  * **Filename Format:** `REQ-[CATEGORY]-[ID].md` (e.g., `REQ-UI-3.md`)
  * **Logseq Page Name:** `[[REQ-UI-3]]`

* **Rules for AI agents (`.roo/rules/`):**

  * **Physical Location:** The files **must** be located in `.roo/rules/`.
  * **Virtual Location in Logseq:** For integration into the knowledge graph, **symbolic links (symlinks)** to each file from `.roo/rules/` must be created in the `pages/` folder.
  * **Symlink Format:** `pages/rules.[rule_name].md` (e.g., `pages/rules.quality-guideline.md`).
  * **Logseq Page Name:** `[[rules/quality-guideline]]`

-----

### 4\. Linking Rules

#### 4.1. Links to Documents in the Knowledge Base

* **Format:** `[[page_name]]`
* **Example:** `This task implements the requirement [[REQ-UI-5]].`

#### 4.2. Links to Code Files, Tests, and Other External Files

* **Principle:** The **Logseq alias** mechanism is used.
* **Format:** `[[relative/path/to/file.py|`file\_name.py`]]`
* **Example:** `The main logic is located in [[b2bfinder/services/search.py|`search.py`]].`

-----

### 5\. Protocol for Structuring Documents and Metadata

Every artifact in the `pages/` directory **must** contain a properties block at the beginning of the file. These properties classify the document and make it machine-readable for queries and automation.

#### 5.1. Properties Schema for a User Story

`STORY-*.md` files must contain the following properties. Using plain text instead of links for `status`, `priority`, and `assignee` is **forbidden**.

```markdown
type:: [[story]]
status:: One of the following values: `[[TODO]]`, `[[DOING]]`, `[[DONE]]`
priority:: One of the following values: `[[high]]`, `[[medium]]`, `[[low]]`
assignee:: Link to the assignee: `[[@username]]`
epic:: Link to the epic: `[[EPIC-NAME]]`
related-reqs:: A comma-separated list of links to requirements: `[[REQ-ID-1]], [[REQ-ID-2]]`
```

#### 5.2. Properties Schema for a Requirement

`REQ-*.md` files must contain the following properties:

```markdown
type:: [[requirement]]
status:: One of the following values: `[[PLANNED]]`, `[[IMPLEMENTED]]`, `[[PARTIAL]]`
```

#### 5.3. Properties Schema for an Implementation Plan

This type of document is created by the `Architect` agent for planning work on an epic or phase.

```markdown
type:: [[implementation-plan]]
phase:: Link to the phase: `[[Phase-5]]`
related-epics:: A comma-separated list of links to epics: `[[EPIC-UI]], [[EPIC-INFRA]]`
status:: One of the following values: `[[DRAFT]]`, `[[APPROVED]]`, `[[COMPLETED]]`
```

-----

### 6\. Project Management and Visualization

#### 6.1. Rule: Mandatory Creation of a Project Hub

A file named `Project Hub.md` **must be** created in the root of the `pages/` directory. It serves as the main entry point for navigating the knowledge base. AI agents must keep it up to date.

**Structure of the `pages/Project Hub.md` file:**

```markdown
title:: Project b2bfinder Hub
---
## 🧭 Navigation
- **Rules and Guidelines:** [[rules.quality-guideline]], [[rules.knowledge-base-standard]]
- **Product:** [[product.vision]], [[requirements]], [[backlog]], [[roadmap]]
- **Technical Documentation:** [[api]], [[caching-strategy]], [[DEPLOYMENT_PLAN]]

---
## 🚀 Development Dashboard
### 👨‍💻 Tasks in Progress (DOING)
{{query (and (property type story) (page-ref "DOING"))}}

### 🔥 Critical Tasks to Do (TODO High Prio)
{{query (and (and (property type story) (page-ref "TODO")) (property priority high))}}
```

#### 6.2. Protocol for Kanban Visualization

For automatic visualization of tasks on a Kanban board (using the Kanban plugin), AI agents must strictly follow these rules.

* **Data Source for Columns:** The `status` property in a User Story is the single source of truth for determining which column of the Kanban board a task is in.
* **Mapping Statuses to Columns:**
  * `status:: [[TODO]]` ➔ **"To Do"** column
  * `status:: [[DOING]]` ➔ **"In Progress"** column
  * `status:: [[DONE]]` ➔ **"Done"** column
* **Data on Cards:** The Kanban plugin should be configured to display the values of the `priority` and `assignee` properties on the cards for quick assessment of the task.
* **Updating:** An AI agent, upon completing a task or starting to work on it, **must** update the `status` property in the corresponding `STORY-*.md` file. The Kanban board on the `[[Project Hub.md]]` page will update automatically.

-----

### 7\. AI Agent Work Protocols

#### 7.1. Work Algorithm (Task Lifecycle)

AI agents are required to follow this algorithm when working on new phases or tasks.

**Phase 1: Analysis and Decomposition**

1. **Input:** Receive a link to a high-level document with tasks (e.g., `[[phase5-implementation-plan]]`).
2. **Action:** Analyze the document. For **each** individual feature or improvement, follow this protocol:
      * Create a new file `pages/STORY-[CATEGORY]-[ID].md`.
      * Fill out the file according to the User Story template, adding the **mandatory properties** from section 5.1.
      * Inside the file, describe the User Story and Acceptance Criteria in detail.
3. **Output:** A set of new, atomic User Story pages in the `pages/` folder.

**Phase 2: Implementation**

1. **Input:** Pick up one User Story with the status `[[TODO]]`.
2. **Action:**
      * **Immediately** update the status in the `STORY-*.md` file to `status:: [[DOING]]`.
      * Proceed with implementing the code and tests.
      * Git commits **must** include the story ID (e.g., `feat: Implement search filters (STORY-API-1)`).
3. **Output:** Completed code that corresponds to the User Story.

**Phase 3: Completion**

1. **Input:** A completed and tested implementation.
2. **Action:**
      * **Immediately** update the status in the `STORY-*.md` file to `status:: [[DONE]]`.
      * Check if the implementation requires updating other documentation and make the necessary changes.
3. **Output:** An updated knowledge base. The dashboards on `[[Project Hub.md]]` will update automatically.

#### 7.2. Protocol for Using Datalog Queries

To obtain global context and analyze relationships, AI agents are **permitted and instructed** to use Datalog queries.

* **Purpose:** Queries are used to retrieve information that is not contained in a single file.
* **Example Scenario:** Before starting work on `[[STORY-API-3]]`, the agent must check the status of the dependent task `[[STORY-INFRA-1]]` by executing the query `{{query (and (page-ref "STORY-INFRA-1") (property type story))}}` and analyzing the `status` property.

#### 7.3. Rule: Contextual Linking

When working on any artifact, the AI agent **must** add links to all related entities: requirements, other tasks, code files, test results.

#### 7.4. Rule: Descriptive Page Names

Page names should be full and descriptive (e.g., `[[Redis Caching Strategy]]` instead of `[[cache]]`).

-----

### 8\. Automation and Validation

#### 8.1. Knowledge Base Linter Script

To maintain the integrity of the knowledge base, the script `scripts/development/validate_kb.py` is used. It should be run in pre-commit hooks and in CI/CD.

#### 8.2. Validation Checklist (for `validate_kb.py`)

The script **must** perform the following checks:

* [ ] **Link Integrity:** All links `[[filename]]` and `[[path/to/code.py|...]]` resolve to existing files.
* [ ] **File Structure:** All documents are created in the correct directories and follow the naming conventions.
* [ ] **Properties Schema:** All User Stories and Requirements have the mandatory properties.
* [ ] **Status Correctness:** The values of the `status` property correspond to the allowed list.
* [ ] **`title` Integrity in READMEs:** All `README.md` files have a `title::` property.
