'''exception.py

Google API errors:
~~~~~~~~~~~~~~~~~~
    - ZeroResultsError
    - OverQueryLimitError
    - RequestDeniedError
    - InvalidRequestError
    - UnknownError

They have supporting class Status. Status is the 1st level container
of Google geo API JSON response, it counterparts to result container.

Note: docstring is needed, despite that explanation mostly duplicated
      in msg class variable because of various helpers in code editors,
      sometimes they show docstring on hover.


Gobject errors:
~~~~~~~~~~~~~~~
    - UnsupportedDataTypeError
'''

from enum import Enum


class ZeroResultsError(Exception):
    '''ZERO_RESULTS exception.
    
    Indicates that the geocode was successful but returned no results.
    This may occur if the geocoder was passed a non-existent address.
    '''
    msg = ('The geocode was successful but returned no results.'
           ' This may occur if the geocoder was passed'
           ' a non-existent address.')


class OverQueryLimitError(Exception):
    '''OVER_QUERY_LIMIT exception.

    Indicates that you are over your quota.
    '''
    msg = 'Over quota.'


class RequestDeniedError(Exception):
    '''REQUEST_DENIED exception.

    Indicates that your request was denied.
    '''
    msg = 'Request denied'


class InvalidRequestError(Exception):
    '''INVALID_REQUEST exception.

    Generally indicates that the query (address, components or lat:lng)
    is missing.
    '''
    msg = 'Query (address, components, lat, lng) is missing'


class UnknownError(Exception):
    '''UNKNOWN_ERROR exception.

    Indicates that the request could not be processed due to a server error.
    The request may succeed if you try again.
    '''
    msg = 'Server error. Try again.'


class Status(Enum):
    '''Enumerable for exceptions which can be received from Google geocode API.

    Standard usecase is just to access class members like in static class:
        Status.STATUS_NAME
    for this statement you do not need class instance. Another usecase must
    be performed with class instance. __init__ initializes Status instance
    with dictionary of exceptions, such that key is exeption string as it
    received from Google API (e.g. "REQUEST_DENIED") and value is a class
    which stands for this status string.

    Example:
    ~~~~~~~~
        We have responce from Google API stored in "data" variable. Data
        is a dictionary with 2 members: result and status.

        >>> data["status"] = "UNKNOWN_ERROR"
        
        >>> for status in Status:
        >>> ....print(status.name, status.value)

        OK 1
        ZERO_RESULTS 2
        OVER_QUERY_LIMIT 3
        REQUEST_DENIED 4
        INVALID_REQUEST 5
        UNKNOWN_ERROR 6
        
        >>> for status in Status:
        ...   if (data['status'] == status.name):
        ...     err = Status(status.value).exception_pool[status.name]
        ...     raise err(err.msg)

        Traceback (most recent call last):
        File "<stdin>", line 4, in <module>
        gobject.exception.UnknownError: Server error. Try again.
    '''
    OK = 1
    ZERO_RESULTS = 2
    OVER_QUERY_LIMIT = 3
    REQUEST_DENIED = 4
    INVALID_REQUEST = 5
    UNKNOWN_ERROR = 6

    def __init__(self, val=1):
        self.exception_pool = {
            'ZERO_RESULTS': ZeroResultsError,
            'OVER_QUERY_LIMIT': OverQueryLimitError,
            'REQUEST_DENIED': RequestDeniedError,
            'INVALID_REQUEST': InvalidRequestError,
            'UNKNOWN_ERROR': UnknownError
        }

    def raise_exception(self):
        exc = self.exception_pool[self.name]
        raise exc(exc.msg)


class UnsupportedDataTypeError(Exception):
    '''Unsupported data error exception.

    Raised when data type / structure is not suitable for the procedure.
    '''
    pass
