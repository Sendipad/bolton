# frappe_workflow_reference.md

## Executive Summary
Frappe’s workflow engine provides a metadata‑driven state machine that enables business processes to be modelled directly on DocTypes. It separates **states**, **transitions**, and **actions**, handling role‑based permissions, conditional evaluation, and automatic field updates. The engine is tightly integrated with both the server (Python) and client (JS/Vue) layers, exposing REST‑style APIs and UI components such as the Workflow Builder.

---

## Architecture Diagram (ASCII)
```
+-------------------+          +-------------------+          +-------------------+
|   DocType (User) |  <--->   |   Workflow Model  |  <--->   |   Workflow Action |
| (Frappe Doc)     |          | (states, trans.)  |          | (tasks, emails)   |
+-------------------+          +-------------------+          +-------------------+
        ^                               ^                               ^
        |                               |                               |
        |                               |                               |
        |                               |                               |
        |                               |                               |
        v                               v                               v
+-------------------+          +-------------------+          +-------------------+
|  Server (Python) |  <--->   |   API / Whitelist|  <--->   |  Scheduler/Queue |
+-------------------+          +-------------------+          +-------------------+
        ^                               ^                               ^
        |                               |                               |
        |                               |                               |
        v                               v                               v
+-------------------+          +-------------------+          +-------------------+
|  Client (JS/Vue) |  <--->   |   Form Toolbar   |  <--->   |  Workflow Builder |
+-------------------+          +-------------------+          +-------------------+
```
---

## Backend Logic Summary
### Core module – `frappe/model/workflow.py`
| Function | Purpose |
|----------|---------|
| `get_workflow(doctype)` | Retrieves the active `Workflow` DocType (cached). |
| `get_transitions(doc, workflow)` | Returns transition dicts allowed for the current state and user roles; evaluates `condition` via `frappe.safe_eval`. |
| `apply_workflow(doc, action)` | Entry point called from UI/whitelisted API. Finds matching transition, checks `has_approval_access`, updates the workflow state field, applies `update_field` from the target state, and moves the document through docstatus changes (draft → submit → cancel). |
| `validate_workflow(doc)` | Ensures the document’s current state is valid and that any state change respects transition rules. |
| `evaluate_condition(transition, doc)` | Uses `frappe.safe_eval` with a safe globals dict (`frappe.db`, `frappe.utils`, `doc`). |
| `enforce_permissions(user, doc, transition)` | Checks role membership (`allowed`), self‑approval flag, and doc‑owner constraints. |

### Performance Optimizations
* **Caching** – workflow name and the full `Workflow` doc are cached via `frappe.cache.hget/hset`. |
* **Lazy loading** – `frappe.model.document.get_doc` loads the document only when needed; transitions are fetched lazily per request. |
* **Bulk DB updates** – When a state change affects many rows (e.g., default state population), a single `UPDATE` query is executed (`frappe.db.sql`). |
* **Docstatus shortcuts** – `apply_workflow` short‑circuits when the doc is already in the target docstatus, avoiding unnecessary `save/submit`. |

### Server Routes (whitelisted methods)
* `/api/method/frappe.workflow.doctype.workflow_action.workflow_action.apply_action` – Called from the UI to present a confirmation page before a transition.
* `/api/method/frappe.workflow.doctype.workflow_action.workflow_action.confirm_action` – Executes the transition after user confirmation.
* Generic REST endpoints `/api/resource/Workflow`, `/api/resource/Workflow Action`, etc., allow CRUD on workflow definitions.

---

## Frontend (Vue + JS) Integration Summary
### Form Toolbar Buttons
* `frappe.ui.form.on('DocType', { refresh: … })` injects **Workflow** buttons based on `doc.get(workflow_state_field)` and the list of allowed transitions returned by `frappe.call('frappe.workflow.get_workflow_state_count')`.
* Clicking a button triggers `frappe.call` to the whitelisted `apply_action` endpoint, which renders a confirmation page (`frappe.respond_as_web_page`).

### Workflow Builder (Vue page)
* Located under `frappe/public/js/workflow_builder/` (not fully listed here). It is a single‑page Vue app bootstrapped by `frappe.ui.make_app_page`. The app fetches the workflow JSON via `frappe.call('frappe.workflow.doctype.workflow.workflow.get_workflow')` and renders draggable state/transition nodes.
* State changes are persisted via `frappe.call` to the `Workflow` DocType, leveraging the same server‑side model.

### Communication Mechanism
* **`frappe.call`** – AJAX POST/GET that sends JSON payloads, receives a response, and updates the UI.
* **Event Bus** – `frappe.events.trigger` is used for real‑time updates (e.g., after a transition, the form reloads). |
* **Realtime** – `frappe.publish_progress` and `frappe.msgprint` provide user feedback during long operations.

---

## API and Routes Summary
| Route | Method | Description |
|-------|--------|-------------|
| `/api/resource/Workflow` | GET/POST/PUT/DELETE | CRUD for workflow definitions. |
| `/api/resource/Workflow Action` | GET/POST/PUT/DELETE | CRUD for pending workflow actions (used by the UI). |
| `/api/method/frappe.workflow.doctype.workflow_action.workflow_action.apply_action` | GET | Render confirmation page for a transition. |
| `/api/method/frappe.workflow.doctype.workflow_action.workflow_action.confirm_action` | POST | Execute the transition (`apply_workflow`). |
| `/api/method/frappe.workflow.doctype.workflow.workflow.get_workflow_state_count` | POST | Returns counts of documents in each state (used by the Builder UI). |
| Generic `/api/method/...` – any whitelisted Python function can be called, enabling custom extensions. |

---

## Important Patterns to Copy for a Custom Rule Engine
1. **Metadata‑Driven Design** – Store states, transitions, and permissions as DocTypes; the engine reads this metadata at runtime.
2. **Separation of Concerns** – Keep **state evaluation**, **permission checks**, and **action execution** in distinct functions (`get_transitions`, `has_approval_access`, `apply_workflow`).
3. **Safe Condition Evaluation** – Use a restricted globals dict (`frappe.safe_eval`) to evaluate user‑defined Python expressions safely.
4. **Server‑Driven UI** – UI components request allowed actions from the server; the server decides based on roles and conditions.
5. **Whitelisted API Endpoints** – Expose only the necessary entry points (`apply_action`, `confirm_action`) while keeping core logic private.
6. **Bulk DB Operations** – When updating many rows (e.g., default state population), use a single `UPDATE` query.
7. **Cache‑First Lookups** – Cache workflow definitions per DocType to avoid repetitive DB hits.
8. **Vue Integration Pattern** – Build a single‑page Vue app that talks to the backend via `frappe.call`, then persists changes back to the same metadata DocTypes.

---

## Pitfalls to Avoid
* **Circular Imports** – The original error (`ModuleNotFoundError`) stemmed from referencing a class as a module path in hooks. Use a top‑level wrapper function or import the class inside the hook.
* **Over‑exposing Whitelisted Methods** – Only expose what the UI needs; otherwise you risk security breaches.
* **Condition Evaluation Overhead** – `frappe.safe_eval` is safe but can be slow if called per‑row; cache evaluated results when possible.
* **State Field Mismatch** – Ensure the custom `workflow_state_field` exists on the target DocType; the `Workflow` DocType automatically creates it if missing.
* **Docstatus Inconsistencies** – Transition logic must correctly handle draft → submit → cancel flows; missing checks lead to illegal state errors.
* **UI Refresh Issues** – After a transition, the form must be reloaded (`frm.reload_doc()`) to reflect the new state.

---

## Final Recommendations for Building a Rule Builder in Vue 3
1. **Adopt the same metadata model** – Define a `RuleEngine` DocType with `states`, `transitions`, and `actions` similar to Frappe’s workflow tables.
2. **Create a top‑level wrapper** – Expose a single whitelisted method `execute_rule(doc, event)` that internally loads the rule engine class (mirroring `RuleCoordinator.execute_rules`).
3. **Leverage Vue 3 Composition API** – Build the visual builder as a Vue 3 component, using `reactive` state for nodes and edges, and `watchEffect` to fetch allowed transitions from the backend.
4. **Use signed URLs for actions** – Follow the pattern of `apply_action`/`confirm_action` with signed parameters to prevent tampering.
5. **Implement safe condition evaluation** – Re‑use Frappe’s `frappe.safe_eval` logic or a sandboxed JS evaluator for rule conditions.
6. **Cache rule definitions** – Store rule metadata in Redis or `frappe.cache`‑like layer to minimise DB queries.
7. **Provide bulk execution APIs** – For mass rule application (similar to `bulk_workflow_approval`), expose a background‑job endpoint.
8. **Testing** – Write unit tests for each transition path, mirroring Frappe’s `test_workflow_*` suites.

---

*This document is intended as a self‑contained reference for developers building a custom rule engine and UI on top of the Frappe framework.*

## How Workflow Executes Many Actions with Conditions

Frappe’s workflow system can **create and run several “Workflow Actions** for a single document transition. The process is driven by metadata (DocTypes) and a few key functions that evaluate conditions, generate actions, and finally execute them.

---

#### 1. Transition → Action Generation

| Step | Function (file) | What it does |
|------|------------------|--------------|
| **a. Find allowed transitions** | `frappe/model/workflow.py → get_transitions()` | Returns a list of transition dicts that match the document’s current state **and** the current user’s roles. For each transition it calls `is_transition_condition_satisfied()` to filter out those whose *condition* expression evaluates to `False`. |
| **b. Create pending actions** | `frappe/workflow/doctype/workflow_action/workflow_action.py → process_workflow_actions()` | After a transition is applied (`apply_workflow`), this function is called. It looks up the **next state** and fetches all *permitted roles* for that state. For every role it inserts a **Workflow Action** row (status = “Open”) that links the document, the transition, and the role. |
| **c. Store the action** | `Workflow Action` DocType | The row contains fields such as `reference_doctype`, `reference_name`, `workflow_state`, `action`, `allowed` (role), and optionally `user` (if a specific user is assigned). This row is the “action” that will later be executed (e.g., send an email, create a task, etc.). |

---

#### 2. Condition Evaluation

* **Where** – `is_transition_condition_satisfied(transition, doc)` (line 91‑96 in `model/workflow.py`).
* **How** – Uses `frappe.safe_eval` with a **restricted globals dict** (`frappe.db`, `frappe.utils`, `doc`) so the condition can be any Python expression the admin writes, e.g.:

```python
condition = "doc.amount > 10000 and doc.customer == 'Acme Corp'"
```

If the expression returns `True`, the transition (and consequently its actions) is kept; otherwise it is discarded.

---

#### 3. Action Execution

| Step | Function (file) | What it does |
|------|------------------|--------------|
| **a. User clicks a button** | UI code in `workflow.js` (client) | The toolbar button calls the whitelisted endpoint `apply_action` → `confirm_action`. |
| **b. Apply the transition** | `apply_workflow()` (model/workflow.py) | Updates the document’s `workflow_state` field, runs any `update_field` logic, changes `docstatus` if needed, and finally calls `doc.add_comment("Workflow", state)`. |
| **c. Process pending actions** | `process_workflow_actions()` (workflow_action.py) | After the state change, this function creates the **Workflow Action** rows for the next state (as described above). |
| **d. Send notifications / run side‑effects** | `send_workflow_action_email()` (workflow_action.py) | If the workflow’s *send_email_alert* flag is set, this function gathers the pending actions, builds a list of recipients (based on permitted roles), and sends an email with links to the actions. |
| **e. Custom “action” code** | You can add a **custom script** to the `Workflow Action` DocType (e.g., a server‑side method that runs when the action’s status changes to “Completed”). The built‑in `apply_action` endpoint simply marks the action as “Completed” and can trigger any extra logic you hook into via `doc_events` or a custom method. |

---

#### 4. Putting It All Together – Example Flow

1. **User opens a Sales Order** – its current workflow state is “Draft”.
2. **Frappe UI** calls `get_transitions()` → returns two possible transitions:  
   * “Submit” (condition: `doc.total > 0`)  
   * “Cancel” (condition: `doc.is_return == 0`)
3. User clicks **Submit** → `apply_action` → `apply_workflow()` updates the state to “Submitted”.
4. `process_workflow_actions()` creates a **Workflow Action** row for each role allowed in the “Submitted” state (e.g., “Sales Manager”, “Accountant”).
5. Because the workflow has *send_email_alert* enabled, `send_workflow_action_email()` sends an email to all users in those roles, each containing a link to **confirm** the action.
6. When a manager clicks the link, `confirm_action` marks the corresponding `Workflow Action` row as “Completed” and can run any custom logic you attached (e.g., generate an invoice).

Thus, **multiple actions** are realized as **multiple rows** in the `Workflow Action` DocType, each generated for a permitted role and each evaluated against the same transition conditions. The engine’s separation of *transition* → *action generation* → *action execution* makes it easy to add extra side‑effects (emails, notifications, background jobs) without cluttering the core transition logic.

---

#### 5. Key Take‑aways for Your Own Rule Engine

| Workflow Feature | Equivalent in a Duplication/Validation Engine |
|------------------|----------------------------------------------|
| **Transition condition** (`is_transition_condition_satisfied`) | **Rule predicate** – evaluate a safe expression against the document. |
| **Workflow Action rows** (`Workflow Action` DocType) | **Pending rule tasks** – create a row per rule (or per role) that needs to be acted on (e.g., “run duplicate check”, “send validation warning”). |
| **Email alert flag** (`send_email_alert`) | **Notification flag** – decide whether to push a message/email after a rule fires. |
| **Permitted roles** (`allowed` field) | **Rule scope** – limit a rule to specific user roles or groups. |
| **process_workflow_actions()** | **generate_rule_tasks()** – after a rule fires, insert task rows for each responsible party. |
| **confirm_action endpoint** | **execute_rule_task()** – endpoint that a user (or a background job) calls to mark the task as done and run the actual logic (e.g., call an external enrichment service). |

By mirroring these patterns—metadata‑driven predicates, safe evaluation, per‑role task generation, and a thin execution endpoint—you can let your rule engine handle **many actions with independent conditions** in a clean, extensible way.

---

## Extended Explanation for Rule Engine (copy‑ready)

I understand – the “Important Patterns to Copy for a Custom Rule Engine” section was written from a workflow‑centric perspective, while your rule engine will focus on things like duplication detection, validation, and data enrichment rather than state transitions.

Here’s a quick re‑framing of the patterns that are still useful for a rule‑engine of that nature, followed by a few additional ideas that map directly to duplication detection, validation, and enrichment:

---

### Core Patterns that Translate Well

| Pattern | How it applies to a duplication/validation/enrichment engine |
|---------|--------------------------------------------------------------|
| **Metadata‑Driven Design** | Define your rules, conditions, and actions as records in DocTypes (e.g. `Rule`, `Rule Condition`, `Rule Action`). The engine reads this metadata at runtime, so you can add or modify rules without code changes. |
| **Separation of Concerns** | Keep three logical layers separate: <br>1. **Rule Retrieval** – fetch applicable rules for a given document.<br>2. **Condition Evaluation** – decide whether a rule fires.<br>3. **Action Execution** – perform the actual duplication check, validation, or enrichment. |
| **Safe Condition Evaluation** | Use a sandboxed evaluator (Frappe’s `frappe.safe_eval` or a similar restricted Python/JS sandbox) to run user‑defined expressions safely. This lets power‑users write custom predicates without exposing the system to arbitrary code execution. |
| **Server‑Driven UI** | The front‑end asks the server “what actions are available for this doc?” and the server returns a list of applicable rule actions. This mirrors how workflow buttons are generated, but the actions can be “Run Duplicate Check”, “Validate Email”, “Enrich Address”, etc. |
| **Whitelisted API Endpoints** | Expose only the minimal set of methods needed by the UI (e.g. `run_rule`, `preview_rule_result`). Keep the core rule‑engine logic private to avoid accidental misuse. |
| **Bulk Operations & Queues** | For large data sets (e.g. batch duplicate detection), enqueue jobs using Frappe’s background‑job system (`frappe.enqueue`). This follows the same pattern used for bulk workflow approvals. |
| **Caching / Lazy Loading** | Cache rule definitions per DocType (`frappe.cache`) so the engine doesn’t hit the database on every document save. Load only the rules that actually apply to the current DocType. |
| **Extensible Hooks** | Provide hook points (e.g. `before_rule_execution`, `after_rule_execution`) that other apps can extend, just like workflow hooks (`doc_events`). |

---

### Additional Patterns Specific to Duplication / Validation / Enrichment

| Feature | Suggested Implementation |
|---------|--------------------------|
| **Duplicate Detection** | • Store a hash or fingerprint of key fields (e.g. email, phone) in a separate “fingerprint” DocType.<br>• In the rule’s action, query this table to find existing records with the same fingerprint.<br>• Return a structured result (match count, IDs) that the UI can display. |
| **Field‑Level Validation** | • Use the same condition‑evaluation engine to express validation rules (e.g. `len(doc.email) > 0 and "@" in doc.email`).<br>• Attach a severity level (`error`, `warning`) to each rule so the UI can decide whether to block save or just warn. |
| **Data Enrichment** | • Actions can call external services (e.g. address verification APIs). Wrap these calls in a helper that logs success/failure and stores enriched data back on the document.<br>• Use Frappe’s `frappe.enqueue` for long‑running enrichment jobs. |
| **Rule Prioritisation** | • Add a `priority` field to the `Rule` DocType. When multiple rules match, execute them in descending priority order. |
| **Result Aggregation** | • After all applicable rules run, collect their outcomes into a single `Rule Engine Result` object attached to the document (e.g. a JSON field). This mirrors how workflow adds a comment after a transition. |
| **User‑Specific Rules** | • Allow rules to be scoped to roles or individual users (`permitted_roles` field). The engine checks the current user’s roles before evaluating a rule, just like workflow permissions. |
| **Audit Trail** | • Insert a `Rule Log` DocType entry for each rule execution (rule name, outcome, timestamp, user). This gives the same traceability that workflow provides via comments. |

---

### Quick Next Steps

1. **Create the core DocTypes** – `Rule`, `Rule Condition`, `Rule Action`, plus optional helper tables (`Fingerprint`, `Rule Log`).  
2. **Implement a generic engine** – a Python function `run_rules(doc, event)` that mirrors `apply_workflow` but iterates over your rule metadata.  
3. **Expose a whitelisted endpoint** – e.g. `frappe.api.run_rules` that the UI can call on save or on demand.  
4. **Build the UI** – use `frappe.ui.form.on` to add a “Run Rules” button that calls the endpoint and displays results (errors, warnings, enrichment data).  

Let me know if you’d like a more detailed design (e.g., exact DocType fields, sample code for the engine, or a UI mock‑up) or if there are any other specific capabilities you have in mind.

---

*This content has been appended to the reference file so you can copy it directly.*
