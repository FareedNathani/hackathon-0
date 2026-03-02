# Skill Name: Task Planner

## Description
This skill provides the procedural knowledge for an AI agent to read tasks from the `vault/Inbox/` folder and create structured execution plans in `vault/Needs_Action/`.

## Workflow
1. **Read Task**
   - **Action:** Open and extract the full content of the markdown file from the `vault/Inbox/` directory.
   - **Goal:** Understand the primary objective and any constraints mentioned in the task.

2. **Analyze Intent**
   - **Action:** Identify the core purpose of the task.
   - **Goal:** Determine if it is a research task, an execution task, a creative task, or a simple information request.

3. **Break into Steps**
   - **Action:** Deconstruct the task into logical, sequential sub-steps.
   - **Goal:** Create a clear path from start to finish to ensure consistency and completeness during execution.

4. **Assign Priority**
   - **Action:** Evaluate the urgency and importance of the task based on keywords like "urgent," "deadline," or "high priority."
   - **Goal:** Set a priority level of High, Medium, or Low.

5. **Check if Human Approval Needed**
   - **Action:** Determine if the task involves sensitive data, significant changes to the codebase, or high-risk operations.
   - **Goal:** Set a flag (Yes/No) to indicate if a human must review the plan before execution.

6. **Save Plan.md to Needs_Action**
   - **Action:** Format the deconstructed plan into a new markdown file.
   - **Goal:** Save the file to `vault/Needs_Action/` with a timestamped name (`Plan_<timestamp>.md`) to ensure it is ready for review or subsequent action.

## Rules and Boundaries
- Only process `.md` files.
- Do not execute the sub-steps in the plan during the planning phase.
- Ensure all plans follow the standardized markdown structure.
