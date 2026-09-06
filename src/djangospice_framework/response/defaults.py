
DEFAULT_RENDERERS = {
    "html": {
        "BACKEND": "djangospice_framework.response.renderers.HTMLRenderer",
    },
    "htmx": {
        "BACKEND": "djangospice_framework.response.renderers.HTMXRenderer",
    },
    "json": {
        "BACKEND": "djangospice_framework.response.renderers.JSONRenderer",
    },
    "text": {
        "BACKEND": "djangospice_framework.response.renderers.TextRenderer",
    },
}

