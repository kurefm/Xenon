# -*- coding: utf-8 -*-


class CookieKindError(AttributeError):

    """An cookie kind error occurred."""


class InfoKindError(AttributeError):

    """An weibo info kind error occurred."""

class NoSectionError(KeyError):
    """Raised when no section matches a requested option."""