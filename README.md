# djangospice-framework

**Application Runtime Framework for building Django apps**

`djangospice-framework` is the application runtime for building modular Django applications.

It provides a consistent foundation for building large Django application ecosystems without repeatedly implementing the same infrastructure in every application.

---

## Why djangospice-framework?

Large Django projects often accumulate infrastructure that gets duplicated across applications.

For example, individual applications may independently implement:

* Base models
* Event dispatching
* Job handling
* File handling
* Import/export pipelines
* Realtime broadcasting
* Common service abstractions

`djangospice-framework` provides these capabilities as a shared runtime.

This gives applications a common architecture and allows modules to remain focused on their actual domain.

### Design goals

* **Reusable** — common functionality should be implemented once.
* **Modular** — functionality should be composed through independent components.
* **Extensible** — applications should be able to replace or extend framework behavior.
* **Django-native** — use Django's existing ecosystem rather than reinventing it.
* **Developer-friendly** — common application infrastructure should require minimal boilerplate.

---

## Requirements

* Python 3.12+
* Django 5.0+

---

## Installation

Install `djangospice-framework` from PyPI:

```bash
pip install djangospice-framework
```

---

## Basic Usage

Once installed, `djangospice-framework` components can be imported by Django applications and modules.

For example, using the common model infrastructure:

```python
from django.db import models

from djangospice_framework.db.models import BaseModel


class Customer(BaseModel):
    name = models.CharField(max_length=255)
```

The exact capabilities available depend on the components being used by the application.

---

# Core Components

`djangospice-framework` is organized around reusable infrastructure rather than business-domain applications.

## Database and Models

Common Django model abstractions provide a consistent foundation for application models.

```python
from djangospice_framework.db.models import BaseModel
```

The database layer is intended to eliminate repetitive model infrastructure while preserving normal Django ORM behavior.

---

## Events

The event system provides a decoupled mechanism for applications to communicate.

Instead of tightly coupling one application component to another, a component can dispatch an event and allow listeners to react to it.

Conceptually:

```text
Application Action
       │
       ▼
     Event
       │
       ├── Listener
       ├── Listener
       └── Listener
```

This allows functionality such as notifications, auditing, integrations, and background processing to be attached without modifying the original application logic.

---

## Broadcasting and Realtime Communication

The runtime provides abstractions for broadcasting application events and data to users or groups.

For example:

```python
Broadcast.everyone(...)
```

or:

```python
Broadcast.user(user, ...)
```

This infrastructure can be used by applications that need realtime updates through WebSockets or other supported transports.

### Client Realtime Events

The framework's client runtime converts server realtime messages into browser `CustomEvent`s.

A server event named:

```text
job_progressed
```

is exposed to the browser as:

```text
djangospice:job_progressed
```

The event name itself is not transformed.

The general mapping is:

```text
Python Event.name
       ↓
WebSocket type
       ↓
djangospice:<event.name>
       ↓
Browser CustomEvent
```

For example:

```text
job_started
      → djangospice:job_started

job_progressed
      → djangospice:job_progressed

job_completed
      → djangospice:job_completed

alert
      → djangospice:alert
```

---

## Client Runtime

The framework includes a small browser-side runtime as Django static assets.

The client runtime provides:

* Realtime WebSocket communication
* Alert dispatching
* Client-side job state management

The JavaScript is included with the Python package and does not require a separate npm package.

### Including the Runtime

The framework JavaScript can be included using Django's static files:

```html
{% load static %}

<script type="module">
    import {
        Realtime,
        Alert,
        Job,
    } from "{% static 'djangospice/js/index.js' %}";
</script>
```

Applications can then configure the client runtime during application startup.

---

## Realtime Client

`Realtime` manages the WebSocket connection and converts incoming server events into browser events.

```javascript
import { Realtime } from "djangospice";

const realtime = new Realtime("/ws/realtime/");

realtime.connect();
```

Once connected, server events are available as browser events.

For example:

```javascript
document.addEventListener(
    "djangospice:job_progressed",
    (event) => {
        console.log(event.detail);
    },
);
```

The realtime client is intentionally domain-agnostic. It does not know how jobs, notifications, or alerts should be rendered.

---

## Alerts

The client `Alert` API connects realtime alert events to application-provided renderers.

It does not implement a specific UI such as a toast, modal, or inline alert.

### Registering a Renderer

```javascript
import { Alert } from "djangospice";

Alert.register(
    "toast",
    new ToastRenderer(),
);

Alert.initialize();
```

A renderer implements a simple `render()` method:

```javascript
class ToastRenderer {
    render(alert, event) {
        // Render the alert using the application's UI.
    }
}
```

The server can specify the renderer:

```json
{
    "type": "alert",
    "alert": {
        "renderer": "toast",
        "level": "success",
        "message": "Export completed successfully."
    }
}
```

The client flow is:

```text
djangospice:alert
       ↓
     Alert
       ↓
renderer: "toast"
       ↓
ToastRenderer
       ↓
Application UI
```

Different renderers can be registered by the application:

```javascript
Alert.register("toast", new ToastRenderer());
Alert.register("modal", new ModalRenderer());
Alert.register("inline", new InlineAlertRenderer());

Alert.initialize();
```

This allows the framework to remain independent of any particular frontend UI library.

---

## Jobs

The client `Job` API maintains the latest state of server-side jobs.

It listens for job lifecycle events and stores the current job state on the client.

### Initialization

```javascript
import { Job } from "djangospice";

Job.initialize();
```

The client automatically handles:

```text
djangospice:job_queued
djangospice:job_started
djangospice:job_progressed
djangospice:job_completed
djangospice:job_failed
```

### Getting a Job

```javascript
const job = Job.get(jobId);

console.log(job.status);
console.log(job.current);
console.log(job.total);
console.log(job.percent);
```

For example:

```javascript
{
    id: "8d4f...",
    name: "reports.ResourceExportJob",
    status: "PROGRESS",
    current: 40,
    total: 100,
    percent: 40
}
```

### Checking for a Job

```javascript
if (Job.has(jobId)) {
    const job = Job.get(jobId);
}
```

### Listing Jobs

```javascript
const jobs = Job.all();
```

This can be used to build a jobs panel or job center:

```javascript
const activeJobs = Job.all().filter(
    (job) => job.status === "PROGRESS",
);
```

### Removing Jobs

```javascript
Job.remove(jobId);
```

To clear all locally stored job state:

```javascript
Job.clear();
```

The client stores the latest job state so that job information can survive page navigation or reloads.

Client-side storage is a cache for continuity. The server remains the authoritative source of job state.

### Job Results

Job completion events include the job's actual result.

For example, a resource export job may return:

```json
{
    "file_url": "/media/exports/students.xlsx",
    "message": "Export completed successfully."
}
```

The result is available through the realtime event:

```javascript
document.addEventListener(
    "djangospice:job_completed",
    (event) => {
        const { job, result } = event.detail;

        console.log(job);
        console.log(result.file_url);
    },
);
```

`Job` manages job state; it does not dictate how jobs are displayed.

Applications can build their own progress bars, job centers, download links, notifications, or other UI on top of the job events and state API.

---

## Recommended Client Initialization

A typical application can initialize the framework client runtime once during startup:

```html
{% load static %}

<script type="module">
    import {
        Realtime,
        Alert,
        Job,
    } from "{% static 'djangospice/js/index.js' %}";

    const realtime = new Realtime("/ws/realtime/");

    realtime.connect();

    Alert.register(
        "toast",
        new ToastRenderer(),
    );

    Alert.initialize();
    Job.initialize();
</script>
```

The application provides the actual UI renderers while `djangospice-framework` provides the runtime and event infrastructure.

---

## Async Support

The runtime provides common abstractions for asynchronous application functionality.

This allows modules to use async operations where appropriate while keeping common infrastructure in one place.

---

## Jobs and Background Processing

The runtime provides infrastructure for dispatching and tracking background jobs.

Jobs can report:

* Queued state
* Started state
* Progress
* Completion
* Failure
* Results

Client applications can consume these updates through the realtime runtime.

---

## Files

`djangospice-framework` provides common abstractions for file-related functionality, allowing applications to work with files without repeatedly implementing storage and file-handling patterns.

---

## Imports and Exports

Reusable import/export infrastructure allows applications to implement data exchange consistently.

Typical use cases include:

* CSV imports
* Spreadsheet imports
* Data exports
* Bulk operations
* Integration pipelines

---

# Application Modules

`djangospice-framework` is **not intended to be a standalone business application**.

Instead, it provides the runtime used by applications and modules.

For example:

```text
djangospice-framework
    │
    ├── billing
    ├── notification
    ├── workflow
    ├── documents
    ├── helpdesk
    ├── CRM
    └── workforce
```

Each application can depend on the common runtime while retaining responsibility for its own domain.

This keeps domain logic out of the framework.

---

# Example

A module can build its domain logic on top of `djangospice-framework`:

```python
from django.db import models

from djangospice_framework.db.models import BaseModel


class Invoice(BaseModel):
    number = models.CharField(
        max_length=50,
        unique=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
```

The module can then use other `djangospice-framework` infrastructure for events, jobs, realtime communication, HTTP responses, tables, files, and other common functionality.

The result is a module that contains primarily **business/domain logic**, rather than infrastructure boilerplate.

---

# License

This package is licensed under the **MIT License**.

See [LICENSE](LICENSE) for the full license text.
