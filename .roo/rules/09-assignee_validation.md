# Assignee Validation Rule

## 1. Purpose

This rule defines the validation requirements for the `assignee` property in User Story documents. The validation ensures that only valid AI agent roles from the approved list in `.roo/rules/05-agent_capabilities.md` can be used in the `assignee::` property of User Stories.

## 2. Valid Assignee Roles

The following AI agent roles are approved for use in the `assignee::` property:

- 🪃 Orchestrator
- 🏗️ Architect
- 💻 Code
- 🪲 Debug
- ❓ Ask
- 🔍 Project Research
- 📝 User Story Creator
- ✍️ Documentation Writer

## 3. Validation Implementation

The assignee validation is implemented in the `scripts/development/validate_kb.py` script. The validation checks that:

1. The `assignee::` property in User Stories follows the correct format: `assignee:: [[@Agent Name]]`
2. The agent name in the assignee property matches one of the approved roles listed above

## 4. Error Handling

When an invalid assignee is detected, the validation script will produce an error message indicating:
- Which User Story file contains the invalid assignee
- What the invalid assignee value is
- A list of valid assignee roles that should be used instead

## 5. Example Valid Assignee Properties

```markdown
assignee:: [[@Code]]
assignee:: [[@Architect]]
assignee:: [[@Documentation Writer]]
```

## 6. Example Invalid Assignee Properties

```markdown
assignee:: [[@InvalidAgent]]  # Invalid - not in approved list
assignee:: Code               # Invalid - wrong format, missing brackets
assignee:: [@Code]            # Invalid - wrong format, missing bracket
```

## 7. Maintenance

When new AI agent roles are added to the system, the validation script and this documentation must be updated to reflect the changes. The validation script automatically extracts the valid roles from `.roo/rules/05-agent_capabilities.md`, so changes to that file will be automatically reflected in the validation.