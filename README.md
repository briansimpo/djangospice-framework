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

Instead of tightly coupling one application component to another, a component can dispatch an event and allow listeners to react.

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

# Client Runtime

The framework includes a small browser-side runtime distributed as Django static assets.

The client runtime provides:

* Realtime WebSocket communication
* Browser `CustomEvent` dispatching
* Alert routing to application-provided renderers
* Client-side job state management
* Job lifecycle events and results
* Local persistence of the latest job state

The JavaScript is included with the Python package and does not require a separate npm package.

The client runtime is intentionally framework-level infrastructure. It does not require a particular frontend framework and does not impose a UI library.

---

## Production Client Setup

The recommended production setup is to initialize the client runtime once from the application's base layout.

Install the package:

```bash
pip install djangospice-framework
```

Configure Django static files normally and collect the framework assets during deployment:

```bash
python manage.py collectstatic
```

Then load the runtime from the package's static assets:

```html
{% load static %}

<script type="module">
    import {
        Realtime,
        Alert,
        Job,
    } from "{% static 'djangospice_framework/js/index.js' %}";
</script>
```

The runtime should normally be initialized once per browser page/application shell rather than independently by individual modules.

---

## Recommended Initialization

A production application should initialize the three client services from its main layout:

```html
{% load static %}

<script type="module">
    import {
        Realtime,
        Alert,
        Job,
    } from "{% static 'djangospice_framework/js/index.js' %}";

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

The application owns the actual renderer implementation and UI. The framework owns the client runtime and event/state infrastructure.

Keep this initialization in one place. Do not create multiple `Realtime` instances for the same application connection unless the application explicitly requires separate realtime channels.

---

# Realtime Client

`Realtime` manages the WebSocket connection and converts incoming server messages into browser events.

```javascript
import { Realtime } from "djangospice_framework";

const realtime = new Realtime("/ws/realtime/");

realtime.connect();
```

The server event name is preserved and exposed using the `djangospice:` browser-event prefix.

For example:

```text
job_started
    ↓
djangospice:job_started

job_progressed
    ↓
djangospice:job_progressed

job_completed
    ↓
djangospice:job_completed
```

Applications can consume events with standard browser event listeners:

```javascript
document.addEventListener(
    "djangospice:job_progressed",
    (event) => {
        const { job } = event.detail;

        console.log(job);
    },
);
```

The realtime client is domain-agnostic. It does not decide whether an event should update a table, progress bar, notification, dashboard, or other UI.

---

## Application Event Handlers

Application code should subscribe to the framework events it needs:

```javascript
function handleJobProgress(event) {
    const { job } = event.detail;

    const progress = document.querySelector(
        `[data-job-id="${job.id}"]`
    );

    if (!progress) {
        return;
    }

    progress.value = job.percent ?? 0;
}

document.addEventListener(
    "djangospice:job_progressed",
    handleJobProgress,
);
```

When registering long-lived listeners from application components, retain the handler reference so it can be removed when the component is destroyed:

```javascript
document.addEventListener(
    "djangospice:job_progressed",
    handleJobProgress,
);

// Later:
document.removeEventListener(
    "djangospice:job_progressed",
    handleJobProgress,
);
```

This prevents duplicate handlers when pages or components are initialized more than once.

---

# Alerts

The client `Alert` API connects realtime alert events to application-provided renderers.

It does not implement a specific UI such as a toast, modal, banner, or inline alert.

## Registering a Renderer

Register the renderers used by the application:

```javascript
import { Alert } from "djangospice_framework";

Alert.register(
    "toast",
    new ToastRenderer(),
);

Alert.register(
    "modal",
    new ModalRenderer(),
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

A renderer should treat the server-provided alert data as input and remain responsible only for presentation.

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

If an application receives an alert for a renderer that it has not registered, the application should ensure that the server only requests renderers supported by the current client.

---

# Jobs

The client `Job` API maintains the latest state of server-side jobs.

It listens for job lifecycle events and stores the current job state on the client.

## Initialization

```javascript
import { Job } from "djangospice_framework";

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

---

## Getting a Job

```javascript
const job = Job.get(jobId);

if (job) {
    console.log(job.status);
    console.log(job.current);
    console.log(job.total);
    console.log(job.percent);
}
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

---

## Checking for a Job

```javascript
if (Job.has(jobId)) {
    const job = Job.get(jobId);

    console.log(job);
}
```

---

## Listing Jobs

```javascript
const jobs = Job.all();
```

For example:

```javascript
const activeJobs = Job.all().filter(
    (job) => job.status === "PROGRESS",
);
```

This can be used to build a jobs panel or job center.

---

## Removing Jobs

Remove one locally stored job:

```javascript
Job.remove(jobId);
```

To clear all locally stored job state:

```javascript
Job.clear();
```

The client stores the latest job state so that job information can survive page navigation or reloads.

Client-side storage is a cache for continuity. The server remains the authoritative source of job state.

---

## Job Lifecycle UI

Applications can build UI directly from the job state and lifecycle events.

For example:

```javascript
document.addEventListener(
    "djangospice:job_progressed",
    (event) => {
        const { job } = event.detail;

        updateProgressBar(
            job.id,
            job.percent,
        );
    },
);
```

Completion can update the UI and expose the result:

```javascript
document.addEventListener(
    "djangospice:job_completed",
    (event) => {
        const { job, result } = event.detail;

        markJobCompleted(job.id);

        if (result?.file_url) {
            showDownloadLink(result.file_url);
        }
    },
);
```

Failure can be handled separately:

```javascript
document.addEventListener(
    "djangospice:job_failed",
    (event) => {
        const { job } = event.detail;

        showJobError(job);
    },
);
```

The framework does not prescribe the UI for any of these states.

---

## Job Results

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

        if (result?.file_url) {
            console.log(result.file_url);
        }
    },
);
```

`Job` manages job state; it does not dictate how job results are displayed.

Applications can build:

* Progress bars
* Job centers
* Download links
* Completion notifications
* Error messages
* Background-operation indicators

on top of the job state and event APIs.

---

# Production Application Pattern

A typical application can keep framework initialization in a single module.

For example:

```javascript
import {
    Realtime,
    Alert,
    Job,
} from "djangospice_framework";

export function initializeDjangospice() {
    const realtime = new Realtime("/ws/realtime/");

    realtime.connect();

    Alert.register(
        "toast",
        new ToastRenderer(),
    );

    Alert.initialize();
    Job.initialize();

    return {
        realtime,
    };
}
```

Then initialize it once from the application's entry point:

```javascript
import { initializeDjangospice } from "./djangospice.js";

initializeDjangospice();
```

This keeps framework startup separate from individual feature modules.

---

# Using the Client with HTMX

The client runtime can be used alongside HTMX.

HTMX remains responsible for HTTP-driven DOM updates while the Djangospice client runtime handles realtime events and client-side state.

For example:

```javascript
document.addEventListener(
    "djangospice:job_completed",
    (event) => {
        const { job } = event.detail;

        if (job.id === currentJobId) {
            htmx.trigger(
                document.body,
                "job-completed",
                { job },
            );
        }
    },
);
```

This allows an application to combine:

```text
Django HTTP
    │
    ├── HTMX → DOM updates
    │
    └── WebSocket → Djangospice client events
                         │
                         ├── Alerts
                         ├── Job state
                         └── Application UI
```

The framework does not require HTMX. This is simply a supported integration pattern for applications that already use it.

---

# Client Runtime Responsibilities

The client runtime is responsible for:

* Establishing the configured realtime connection
* Receiving server realtime messages
* Converting server events into browser `CustomEvent`s
* Routing alert events to registered renderers
* Maintaining the latest client-side job state
* Exposing job lifecycle information to application code

The application remains responsible for:

* UI rendering
* Toast/modal implementations
* Progress bars
* Job centers
* Page-specific event handling
* Navigation
* Application-specific error presentation
* Authentication and authorization configuration
* Deployment-specific WebSocket routing

This separation keeps `djangospice-framework` independent of a particular frontend application.

---

# Client Event Contract

The stable browser event contract is:

```text
djangospice:<event.name>
```

where `<event.name>` is the server event name.

For example:

```text
Python Event.name
        ↓
WebSocket message
        ↓
djangospice:<event.name>
        ↓
Browser CustomEvent
```

Applications should subscribe to the public `djangospice:*` events rather than depending on internal client implementation details.

---

# Async Support

The runtime provides common abstractions for asynchronous application functionality.

This allows modules to use async operations where appropriate while keeping common infrastructure in one place.

---

# Jobs and Background Processing

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

# Files

`djangospice-framework` provides common abstractions for file-related functionality, allowing applications to work with files without repeatedly implementing storage and file-handling patterns.

---

# Imports and Exports

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
