from __future__ import annotations

import json
from dataclasses import dataclass, field
from html import escape
from typing import Any, ClassVar, Literal, Self

from djangospice_framework.core.payload import Payload
from djangospice_framework.core.serializable import Serializable

HTTPMethod = Literal["get", "post", "put", "patch", "delete"]


@dataclass(slots=True)
class HTMXAttributes(Serializable):
    """Represents HTMX HTML attributes with a fluent builder interface.

    This class is transport-agnostic and compiles cleanly into standard HTML attribute
    strings or dictionaries for:
    - Widgets
    - Forms
    - Components
    - Views
    - Template rendering
    """

    # ------------------------------------------------------------------
    # Standard HTML
    # ------------------------------------------------------------------

    id: str | None = None
    """Optional `id` attribute."""

    css_class: str = ""
    """Space-separated string of CSS classes (`class` attribute)."""

    attrs: Payload = field(default_factory=Payload)
    """Additional standard HTML attributes (e.g., placeholder, name)."""

    # ------------------------------------------------------------------
    # Swapping
    # ------------------------------------------------------------------

    target: str | None = None
    """CSS selector targeting the element to swap (`hx-target`)."""

    swap: str | None = None
    """Swap strategy (e.g., `outerHTML`, `innerHTML`) (`hx-swap`)."""

    swap_oob: str | None = None
    """Out-of-band swap instructions (`hx-swap-oob`)."""

    select: str | None = None
    """CSS selector choosing content from the response (`hx-select`)."""

    select_oob: str | None = None
    """Out-of-band selection selector (`hx-select-oob`)."""

    # ------------------------------------------------------------------
    # Triggers & Execution
    # ------------------------------------------------------------------

    trigger: str | None = None
    """Event trigger configuration (`hx-trigger`)."""

    sync: str | None = None
    """Request synchronization rules (`hx-sync`)."""

    disable: bool | None = None
    """Disables HTMX processing on element/children (`hx-disable`)."""

    disinherit: str | None = None
    """Disinherits HTMX attributes from parent elements (`hx-disinherit`)."""

    # ------------------------------------------------------------------
    # Navigation & History
    # ------------------------------------------------------------------

    push_url: bool | str | None = None
    """Pushes a URL into browser history (`hx-push-url`)."""

    replace_url: bool | str | None = None
    """Replaces the current URL in browser history (`hx-replace-url`)."""

    boost: bool | None = None
    """Enables progressive enhancement for links and forms (`hx-boost`)."""

    history: bool | None = None
    """Prevents snapshotting historical states (`hx-history`)."""

    history_elt: bool | None = None
    """Marks element for history snapshot caching (`hx-history-elt`)."""

    # ------------------------------------------------------------------
    # Request Configuration
    # ------------------------------------------------------------------

    include: str | None = None
    """CSS selector for additional element values to include (`hx-include`)."""

    params: str | None = None
    """Filters parameters submitted with the request (`hx-params`)."""

    vals: Payload | str | dict = field(default_factory=Payload)
    """Values submitted with the request (`hx-vals`). Supports dicts or raw `js:` strings."""

    headers: Payload | str | dict = field(default_factory=Payload)
    """Request headers sent with the HTMX request (`hx-headers`)."""

    encoding: str | None = None
    """Request body encoding type (`hx-encoding`)."""

    ext: str | None = None
    """HTMX extensions enabled on this element (`hx-ext`)."""

    # ------------------------------------------------------------------
    # UX & Feedback
    # ------------------------------------------------------------------

    indicator: str | None = None
    """CSS selector for a loading indicator element (`hx-indicator`)."""

    disabled_elt: str | None = None
    """Elements to disable during the request lifecycle (`hx-disabled-elt`)."""

    confirm: str | None = None
    """Confirmation dialog prompt message (`hx-confirm`)."""

    prompt: str | None = None
    """JavaScript prompt input box message (`hx-prompt`)."""

    preserve: bool | None = None
    """Preserves element state across swaps (`hx-preserve`)."""

    # ------------------------------------------------------------------
    # Events & Websockets
    # ------------------------------------------------------------------

    on: Payload = field(default_factory=Payload)
    """Inline event handlers mapped to `hx-on:*` attributes."""

    ws: str | None = None
    """WebSocket connection target (`hx-ws`)."""

    sse: str | None = None
    """Server-Sent Events source (`hx-sse`)."""

    # ------------------------------------------------------------------
    # Mapping
    # ------------------------------------------------------------------

    ATTRIBUTE_MAP: ClassVar[dict[str, str]] = {
        # Requests
        "get": "hx-get",
        "post": "hx-post",
        "put": "hx-put",
        "patch": "hx-patch",
        "delete": "hx-delete",
        # Swapping
        "target": "hx-target",
        "swap": "hx-swap",
        "swap_oob": "hx-swap-oob",
        "select": "hx-select",
        "select_oob": "hx-select-oob",
        # Triggers
        "trigger": "hx-trigger",
        "sync": "hx-sync",
        "disable": "hx-disable",
        "disinherit": "hx-disinherit",
        # Navigation
        "push_url": "hx-push-url",
        "replace_url": "hx-replace-url",
        "boost": "hx-boost",
        "history": "hx-history",
        "history_elt": "hx-history-elt",
        # Request configuration
        "include": "hx-include",
        "params": "hx-params",
        "encoding": "hx-encoding",
        "ext": "hx-ext",
        "ws": "hx-ws",
        "sse": "hx-sse",
        # UX
        "indicator": "hx-indicator",
        "disabled_elt": "hx-disabled-elt",
        "confirm": "hx-confirm",
        "prompt": "hx-prompt",
        "preserve": "hx-preserve",
    }

    # ------------------------------------------------------------------
    # Fluent API Builders
    # ------------------------------------------------------------------

    def request(self, method: HTTPMethod | str, url: str) -> Self:
        """Sets the HTMX request method and destination URL."""
        method_lower = method.lower()
        if method_lower not in {"get", "post", "put", "patch", "delete"}:
            raise ValueError(f"Unsupported HTMX request method: {method}")
        setattr(self, method_lower, url)
        return self

    def get(self, url: str) -> Self:
        """Shorthand for `request('get', url)`."""
        return self.request("get", url)

    def post(self, url: str) -> Self:
        """Shorthand for `request('post', url)`."""
        return self.request("post", url)

    def put(self, url: str) -> Self:
        """Shorthand for `request('put', url)`."""
        return self.request("put", url)

    def patch(self, url: str) -> Self:
        """Shorthand for `request('patch', url)`."""
        return self.request("patch", url)

    def delete(self, url: str) -> Self:
        """Shorthand for `request('delete', url)`."""
        return self.request("delete", url)

    def swap_to(self, strategy: str) -> Self:
        """Sets the `hx-swap` strategy."""
        self.swap = strategy
        return self

    def target_to(self, selector: str) -> Self:
        """Sets the `hx-target` selector."""
        self.target = selector
        return self

    def trigger_on(self, trigger: str) -> Self:
        """Sets the `hx-trigger` event rules."""
        self.trigger = trigger
        return self

    def include_data(self, selector: str) -> Self:
        """Sets the `hx-include` selector for extra payload fields."""
        self.include = selector
        return self

    def show_indicator(self, selector: str) -> Self:
        """Sets the `hx-indicator` loading element selector."""
        self.indicator = selector
        return self

    def confirm_with(self, message: str) -> Self:
        """Sets an `hx-confirm` dialog prompt before request execution."""
        self.confirm = message
        return self

    def push(self, url: bool | str = True) -> Self:
        """Updates the browser's history URL (`hx-push-url`)."""
        self.push_url = url
        return self

    def with_vals(self, raw_js_str: str | None = None, **kwargs: Any) -> Self:
        """Merges values into `hx-vals`.

        Pass `raw_js_str="js:{myVar: getVar()}"` to evaluate native JavaScript.
        """
        if raw_js_str:
            self.vals = raw_js_str
        elif isinstance(self.vals, (Payload, dict)):
            self.vals.update(kwargs)
        else:
            self.vals = Payload(kwargs)
        return self

    def add_class(self, *classes: str) -> Self:
        """Appends unique CSS classes while maintaining insertion order."""
        if not classes:
            return self

        current_classes = self.css_class.split()
        new_classes = [c for chunk in classes for c in chunk.split() if c]

        seen = set()
        unique_ordered = [
            c for c in (current_classes + new_classes)
            if not (c in seen or seen.add(c))
        ]

        self.css_class = " ".join(unique_ordered)
        return self

    def attr(self, name: str, value: Any) -> Self:
        """Injects a custom non-HTMX standard HTML attribute."""
        self.attrs[name] = value
        return self

    def event(self, name: str, handler: str) -> Self:
        """Binds an inline event handler to `hx-on:{name}`."""
        self.on[name] = handler
        return self

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serializes attributes into a clean dictionary of final HTML attributes."""
        data: dict[str, Any] = dict(self.attrs) if self.attrs else {}

        if self.id:
            data["id"] = self.id
        if self.css_class:
            data["class"] = self.css_class

        for field_name, html_name in self.ATTRIBUTE_MAP.items():
            value = getattr(self, field_name)
            if value is None:
                continue

            # HTMX expects explicit lowercase string "true"/"false" for booleans
            if isinstance(value, bool):
                data[html_name] = str(value).lower()
            else:
                data[html_name] = value

        if self.vals:
            data["hx-vals"] = self.vals if isinstance(self.vals, str) else json.dumps(self.vals)

        if self.headers:
            data["hx-headers"] = self.headers if isinstance(self.headers, str) else json.dumps(self.headers)

        for event, handler in self.on.items():
            data[f"hx-on:{event}"] = handler

        return data

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> str:
        """Renders attributes directly into a safe, escaped HTML attribute string."""
        html_parts = []
        for key, value in self.to_dict().items():
            if isinstance(value, bool):
                if value:
                    html_parts.append(key)
                continue

            html_parts.append(f'{key}="{escape(str(value), quote=True)}"_{""}')

        return " ".join(html_parts)

    # ------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------

    def __bool__(self) -> bool:
        """Optimized truthiness validation avoiding heavy JSON serialization."""
        return bool(
            self.id
            or self.css_class
            or self.vals
            or self.headers
            or self.on
            or self.attrs
            or any(getattr(self, f) is not None for f in self.ATTRIBUTE_MAP)
        )

    def __html__(self) -> str:
        return self.render()

    def __str__(self) -> str:
        return self.render()