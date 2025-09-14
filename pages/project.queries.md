---
title:: Project Queries Documentation
---

type:: [[documentation]]
category:: [[queries]]
purpose:: [[centralized-query-library]]
status:: [[active]]

# Project Queries Library

This page serves as the central repository for all Logseq queries used across the project's knowledge base. These queries power the dynamic dashboards and automated reporting features of the Project Hub.

## Query Categories

### Health Monitoring Queries

These queries monitor the overall health and integrity of the knowledge base:

- **Orphaned Artifacts**: Identifies tasks without assignees and requirements without linked stories
- **Stale Knowledge**: Finds documents that haven't been updated recently and may need review
- **Broken Links**: Detects references to non-existent pages or resources

### Strategic Overview Queries  

High-level queries for project management and strategic decision-making:

- **Epic Status Overview**: Shows current status of all project epics
- **Learning Dashboard**: Aggregates lessons learned across phases
- **Deadline Tracking**: Monitors upcoming deadlines and deliverables
- **Progress Metrics**: Calculates completion rates and velocity metrics

### Development Dashboard Queries

Operational queries for daily development work:

- **Task Board**: Shows tasks by status (TODO, DOING, DONE)
- **Blocked Items**: Identifies tasks that are currently blocked
- **Review Queue**: Lists items awaiting review or approval
- **Recent Activity**: Shows recently completed work

## Query Implementation

All queries follow the Logseq query syntax and are designed to be:

- **Reusable**: Can be embedded in multiple locations
- **Maintainable**: Centralized location for easy updates
- **Consistent**: Standardized naming and structure
- **Performant**: Optimized for quick execution

## Usage Instructions

To use these queries in other pages:

1. Reference the specific query section using `{{embed [[project.queries]]#query-id}}`
2. Ensure the target page has the required properties for the query to work
3. Test queries in a development environment before production use

## Maintenance

This library should be updated when:
- New query requirements emerge
- Existing queries need optimization
- Property schemas change in the knowledge base
- New dashboard features are requested

## Related Documentation

- Project Hub - Main dashboard that uses these queries
- Logseq Query Documentation - Technical reference for query syntax
- Knowledge Base Schema - Property definitions used in queries