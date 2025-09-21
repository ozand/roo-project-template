# Implementation Specification Template

This template is designed for creating detailed technical specifications before development begins. Using this template is mandatory for all complex User Stories and follows the **spec-driven workflow** principles.

---

## Basic Template

```markdown
# specs.STORY-[CATEGORY]-[ID]

type:: [[implementation-spec]]
related-story:: [[STORY-CATEGORY-ID]]
status:: [[DRAFT]]
architect:: [[@username]]
created-date:: [[YYYY-MM-DD]]
review-required:: [[true]]
complexity:: [[medium]]

---

## 🎯 Goal and Context

**Related User Story:** [[STORY-CATEGORY-ID]]

**Brief Description:**
- What exactly will be implemented
- Why this is necessary
- How this fits into the overall architecture

## 📋 Technical Requirements

### Functional Requirements
- [ ] Requirement 1
- [ ] Requirement 2
- [ ] Requirement 3

### Non-Functional Requirements
- **Performance:** 
- **Security:** 
- **Scalability:** 
- **Compatibility:** 

## 🏗️ Architectural Solution

### Component Overview
```
[Architecture diagram or schema]
```

### Key Components
1. **Component A:**
   - Purpose:
   - Interfaces:
   - Dependencies:

2. **Component B:**
   - Purpose:
   - Interfaces:
   - Dependencies:

## 🔧 Implementation Details

### API Contracts
```typescript
interface ExampleInterface {
    method(param: string): Promise<Result>;
}
```

### Data Schema
```sql
-- Data schema examples, if needed
```

### Configuration
- Configuration parameters
- Environment variables
- Default settings

## 🧪 Testing Plan

### Unit Tests
- [ ] Test for function A
- [ ] Test for function B
- [ ] Test for error handling

### Integration Tests
- [ ] Integration test with component X
- [ ] Integration test with external API

### E2E Tests
- [ ] Use case scenario 1
- [ ] Use case scenario 2

## 📁 File Structure

```
src/
├── components/
│   ├── ComponentA.ts
│   └── ComponentB.ts
├── types/
│   └── interfaces.ts
├── tests/
│   ├── ComponentA.test.ts
│   └── ComponentB.test.ts
└── index.ts
```

## ⚠️ Risks and Limitations

### Technical Risks
- Risk 1: Description and mitigation plan
- Risk 2: Description and mitigation plan

### Limitations
- Limitation 1
- Limitation 2

## 🔄 Implementation Plan

### Phase 1: Preparation
- [ ] Environment setup
- [ ] Create basic structure

### Phase 2: Core Implementation
- [ ] Implement component A
- [ ] Implement component B
- [ ] Integrate components

### Phase 3: Testing and Refinement
- [ ] Unit tests
- [ ] Integration tests
- [ ] Fix found defects

### Phase 4: Finalization
- [ ] Documentation
- [ ] Code review
- [ ] Release preparation

## ✅ Definition of Done

### Completion Criteria
- [ ] All functional requirements implemented
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] No critical security vulnerabilities

---

## Additional Notes

[Here can be placed any additional notes, links to useful resources, or special considerations]
```

---

## Usage Recommendations

1. **Creation:** The `Architect` agent creates the specification immediately after User Story analysis
2. **Statuses:** 
   - `[[DRAFT]]` - draft, requires refinement
   - `[[APPROVED]]` - approved for implementation
   - `[[COMPLETED]]` - implementation completed
3. **Review:** For complex specifications, set `review-required:: [[true]]`
4. **Updates:** Specification can be updated during implementation, but critical changes require changing status back to `[[DRAFT]]`

---

*This template is integrated with the AI Agent Constitution and follows spec-driven workflow principles from the github-spec-kit project.*