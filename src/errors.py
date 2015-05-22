# -*- coding: utf-8 -*-

import common


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


class TimeOutError(XenonError):
    """Out of timeout time and times setting"""

    def __init__(self):
        message = \
            'Out of timeout time and times setting! timeout {0} sec, retry {1} times.'. \
                format(common.HTTP_TIMEOUT, common.HTTP_TIMEOUT_RETRY_TIMES)
        super(TimeOutError, self).__init__(message)


class SearchStartAtError(XenonError):
    """ """


class SearchPageError(XenonError):
    """ """

    def __init__(self, error_page, *args, **kwargs):
        super(SearchPageError, self).__init__(*args, **kwargs)
        self.error_page = error_page


class SearchPageResolveError(XenonError):
    """ """


class GetHostWordsError(XenonError):
    """ """
