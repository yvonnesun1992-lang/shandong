from __future__ import annotations

import math


def paginate_items(items: list, page: int = 1, page_size: int = 20) -> dict:
    safe_items = list(items or [])
    safe_page_size = min(max(int(page_size or 20), 1), 100)
    total = len(safe_items)
    total_pages = math.ceil(total / safe_page_size) if total else 0
    safe_page = max(int(page or 1), 1)
    if total_pages:
        safe_page = min(safe_page, total_pages)
    else:
        safe_page = 1
    start = (safe_page - 1) * safe_page_size
    end = start + safe_page_size
    return {
        "items": safe_items[start:end],
        "pagination": {
            "page": safe_page,
            "page_size": safe_page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": bool(total_pages and safe_page < total_pages),
            "has_prev": bool(total_pages and safe_page > 1),
        },
    }
