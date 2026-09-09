# djangospice-framework

**Application Runtime Framework for building Django apps**

`djangospice-framework` is the application runtime for building modular Django applications.

It is designed to provide a consistent foundation for building large Django application ecosystems without repeatedly implementing the same infrastructure in every application.

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

djangospice-framework is designed around several principles:

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

Install djangospice-framework from PyPI:

```bash
pip install djangospice-framework
```

---

## Basic Usage

Once installed, djangospice-framework components can be imported by Django applications and modules.

For example, using the common model infrastructure:

```python
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

---

## Async Support

The runtime provides common abstractions for asynchronous application functionality.

This allows modules to use async operations where appropriate while keeping common infrastructure in one place.

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
    ├── workforce
```

Each application can depend on the common runtime while retaining responsibility for its own domain.

This keeps domain logic out of the framework.

---

# Example

A module can build its domain logic on top of `djangospice-framework`:

```python
from djangospice_framework.db.models import BaseModel


class Invoice(BaseModel):
    number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
```

The module can then use other `djangospice-framework` infrastructure for events, notifications, UI, HTTP responses, tables, files, and other common functionality.

The result is a module that contains primarily **business/domain logic**, rather than infrastructure boilerplate.

---

# License

This package is licensed under the **MIT License**.

See [LICENSE](LICENSE) for the full license text.
