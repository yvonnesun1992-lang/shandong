from __future__ import annotations

from dataclasses import dataclass

from src.core.account import AccountContext, create_account_context
from src.core.user_context import UserContext


@dataclass
class User:
    user_id: str
    role: str = "user"
    display_name: str | None = None
    is_authenticated: bool = True

    def __post_init__(self) -> None:
        account = create_account_context(self.user_id)
        self.user_id = account.user_id
        if self.display_name is None:
            self.display_name = self.user_id

    @property
    def account(self) -> AccountContext:
        return create_account_context(self.user_id)

    @property
    def context(self) -> UserContext:
        return UserContext(self.user_id)

    def as_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "role": self.role,
            "display_name": self.display_name,
            "is_authenticated": self.is_authenticated,
            "account": self.account.as_dict(),
        }


class SessionManager:
    def __init__(self) -> None:
        self._current_user: User | None = None

    def login(self, user_id: str, role: str = "user", display_name: str | None = None) -> User:
        user = User(user_id=user_id, role=role, display_name=display_name, is_authenticated=True)
        self._current_user = user
        return user

    def logout(self) -> bool:
        had_user = self._current_user is not None
        self._current_user = None
        return had_user

    def current_user(self) -> User | None:
        return self._current_user

    def user_context(self) -> UserContext:
        if self._current_user is None:
            return UserContext("anonymous")
        return self._current_user.context


_DEFAULT_SESSION = SessionManager()


def login(user_id: str, role: str = "user", session_manager: SessionManager | None = None) -> User:
    manager = session_manager or _DEFAULT_SESSION
    return manager.login(user_id=user_id, role=role)


def logout(session_manager: SessionManager | None = None) -> bool:
    manager = session_manager or _DEFAULT_SESSION
    return manager.logout()
