# Skill: File Triage (Bronze Tier)

## Overview
This skill defines the process for an AI agent to monitor, analyze, and categorize new tasks entering the system via the `vault/Inbox/` folder.

## Procedural Steps

### 1. Read Task from Inbox
- **Action:** Open and read any new markdown file (`.md`) placed within the `vault/Inbox/` directory.
- **Goal:** Extract the full text and any metadata (if present) to understand the user's request or the task's context.

### 2. Summarize Task
- **Action:** Analyze the content extracted in Step 1.
- **Goal:** Create a concise summary (1-3 sentences) that captures the core objective, any deadlines, and key stakeholders mentioned.

### 3. Categorize Task
- **Action:** Based on the summary and original content, determine the appropriate next state.
- **Decision Logic:**
  - **Needs Action:** If the task requires further research, follow-up, or execution of a multi-step process.
  - **Done:** If the task is a simple confirmation, a piece of information already processed, or a completed activity that only requires archiving.

### 4. Write Output Markdown
- **Action:** Create a new markdown file in the target directory based on the categorization.
- **Destination:**
  - `vault/Needs_Action/` (for tasks requiring action)
  - `vault/Done/` (for completed tasks)
- **Format:**
  - **Title:** Use the original filename prefixed with the category.
  - **Content:** Include the original text, followed by the generated summary, and a "Next Steps" section if categorized as "Needs Action".

## Rules and Boundaries
- Only process `.md` files.
- Do not delete the original file from `vault/Inbox/` unless explicitly instructed (for Bronze tier, assume persistence or manual cleanup).
- Maintain consistent formatting across all output files.
