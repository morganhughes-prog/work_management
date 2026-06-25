# Mapping Extract to DevOps (Planner → work_management)

## Overview
This document defines the mapping from a Planner extract dataset into the `work_management` system. It includes:

- Field-by-field mapping  
- Target tables  
- Fields to ignore  
- Minimal schema extensions  
- Transformation logic  

---

## 1. Dataset Summary

The Planner extract contains:

**Structure**
- ~1,143 rows, 43 columns  
- Hierarchical + task-based  

### Key Components

**Hierarchy**
- Primary Name → program/area (e.g. GSI - Section Management)  
- Secondary Name → sub-area (e.g. GSI - HR)  
- Outline Number → grouping structure  

**Tasks**
- Name → task titles  
- Bucket → workflow column  
- Status → completion state  

**Operational Data**
- Assigned user  
- Dates (start, finish, resolution)  
- Work Type (critical for reporting)  

---

## 2. Core Mapping to work_management

### Tasks Table

| Planner Field | Target Field | Notes |
|--------------|-------------|-------|
| Name | title | Core |
| Definition of done | description | Optional |
| Notes | description (append) | Optional |
| Bucket | status | Map to workflow |
| Status | status (override) | Use if better |
| Assigned to | owner_id | Requires mapping |
| Start | start_date | |
| Finish | due_date | |
| Resolution / NFA Date | completed_date | |
| Work Type | work_type_id | Key reporting |
| Task number | external_id | Traceability |

---

### Work Types

| Planner Field | Target |
|--------------|--------|
| Work Type | name |

---

### Projects (New)

| Planner Field | Target |
|--------------|--------|
| Primary Name | project_name |
| Secondary Name | sub_project |

Link:

```
tasks.project_id → projects.id
```

---

### Users

| Planner Field | Target |
|--------------|--------|
| Assigned to | users.name |

Example:

```python
USER_MAP = {
    "Gina ROCKS": 1,
    "Pratika DLIMA": 2
}
```

---

## 3. Fields to Drop

- Outline Number
- Index fields
- Header flags
- % Complete
- Effort
- Dependencies
- Checklist items

---

## 4. Status Mapping

```python
STATUS_MAP = {
    "Not Started": "todo",
    "In Progress": "doing",
    "Completed": "done",
    "Resolved": "done"
}

BUCKET_MAP = {
    "Personal": "todo",
    "In Progress": "doing",
    "Complete": "done"
}
```

---

## 5. Transformation Logic

### Filter Tasks

```python
df = df[df["Is Primary Header"] == False]
df = df[df["Name"].notna()]
```

### Map Fields

```python
df["title"] = df["Name"]
df["status"] = df["Status"].map(STATUS_MAP).fillna(df["Bucket"].map(BUCKET_MAP))
```

---

## Final Summary

Planner Export → Relational System

Task = Work + Owner + Status + Work Type + Project
