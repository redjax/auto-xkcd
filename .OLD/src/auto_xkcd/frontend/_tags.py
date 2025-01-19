from __future__ import annotations

CUSTOM_FRONTEND_TAGS: list[dict[str, str]] = [
    {
        "name": "testing",
        "description": "[Only mounted in DEV environment] Ephemeral test routes for testing ideas before committing fully.",
    },
    # {"name": "comic", "description": "Endpoints for XKCD comic interactions."},
    # {
    #     "name": "task",
    #     "description": "Interact with background tasks, i.e. comic retrievals or data tasks.",
    # },
    # {
    #     "name": "admin",
    #     "description": "[Only mounted in DEV environment] A backend admin route handler.",
    # },
]
