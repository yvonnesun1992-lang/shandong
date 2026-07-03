from __future__ import annotations

from guided_setup.init import boundary


def explain_why_3000_not_open(requirements: dict) -> list[str]:
    blocker = requirements.get("likely_blocker", "")
    return [
        "3000 is the frontend web page service.",
        "If 127.0.0.1:3000 does not open, the frontend is usually not running.",
        f"Current likely blocker: {blocker}",
    ]


def explain_backend_vs_frontend() -> list[str]:
    return [
        "3000 is the frontend page you open in the browser.",
        "8000 is the backend API service used by the frontend.",
        "Python backend passing TestClient means the code is valid, but it does not mean the browser page has started.",
    ]


def explain_what_node_does() -> list[str]:
    return ["Node.js is the tool needed to run the web frontend."]


def explain_what_pnpm_does() -> list[str]:
    return ["pnpm is the tool that installs and runs frontend dependencies."]


def explain_what_to_do_next(requirements: dict) -> list[str]:
    blocker = requirements.get("likely_blocker", "")
    if "Node.js" in blocker:
        return ["Install Node.js LTS manually, reopen the terminal, then run node -v."]
    if "pnpm" in blocker:
        return ["Run npm install -g pnpm, then run pnpm -v."]
    if "dependencies" in blocker:
        return ["Run cd web/frontend && pnpm install."]
    if "frontend dev server" in blocker:
        return ["Run cd web/frontend && pnpm dev --hostname 127.0.0.1 --port 3000."]
    return ["Follow the Mac or Windows setup steps in order."]


def build_plain_language_summary(requirements: dict) -> dict:
    lines = (
        explain_why_3000_not_open(requirements)
        + explain_backend_vs_frontend()
        + explain_what_node_does()
        + explain_what_pnpm_does()
        + explain_what_to_do_next(requirements)
    )
    return {"plain_language_summary": lines, "recommended_next_step": explain_what_to_do_next(requirements)[0], **boundary()}
