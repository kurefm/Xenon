# -*- coding: utf-8 -*-

class XenonError(StandardError):
    """All error' superclass """


class CookieKindError(XenonError):
    """An cookie kind error occurred."""


class InfoKindError(XenonError):
    """An weibo info kind error occurred."""


class NoSectionError(XenonError):
    """Raised when no section matches a requested option."""


class LoginError(XenonError):
    """Can't login"""
