"""
Exceptions for sensing service application
"""

import json

DEVELOPER_MESSAGE_KEY = 'developer_message'
USER_MESSAGE_KEY = 'user_message'
MORE_INFO_KEY = 'more_info'
CONTEXT_KEY = 'context'


class InfoException(Exception):
    """
    Generic exception including info dictionary used to be derived by more
    specific exceptions.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        self.info = info
        super(InfoException, self).__init__(self.info[CONTEXT_KEY])

    def information(self):
        """
        Return info dictionary
        """

        return self.info

    def __str__(self):
        return json.dumps(self.info)


class GeneralInfoException(InfoException):
    """
    Used by presentation layer when a general Exception is caught.
    It may be used to translate a standard python exception into an info exception.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'Exception occurred'
        self.info[USER_MESSAGE_KEY] = 'Service error'
        self.info[CONTEXT_KEY] = context

        super(GeneralInfoException, self).__init__(self.info)


class BadRequestBase(InfoException):
    """
    Inherit from this exception to create exceptions where the error is in user request.
    Error code for exceptions derived from this one should start with 400.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        super(BadRequestBase, self).__init__(info)


class BadRequest(BadRequestBase):
    """
    Used to notify a general bad request.
    context should include argument name for all offending arguments.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'An invalid request was provided'
        self.info[USER_MESSAGE_KEY] = 'An invalid request was provided'
        self.info[CONTEXT_KEY] = context

        super(BadRequest, self).__init__(self.info)


class InvalidArgument(BadRequestBase):
    """
    Used to notify invalid arguments.
    context should include argument name for all offending arguments.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'An invalid argument was provided'
        self.info[USER_MESSAGE_KEY] = 'An invalid argument was provided'
        self.info[CONTEXT_KEY] = context

        super(InvalidArgument, self).__init__(self.info)


class MissingArgumentValue(BadRequestBase):
    """
    Used to notify valid arguments with required but missing value.
    context should include argument name for all offending arguments.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'No value provided for an argument with required value'
        self.info[USER_MESSAGE_KEY] = 'No value provided for an argument with required value'
        self.info[CONTEXT_KEY] = context

        super(MissingArgumentValue, self).__init__(self.info)


class InvalidArgumentValue(BadRequestBase):
    """
    Used to notify valid arguments with invalid values.
    context should include argument name, actual value and allowed values for all offending arguments.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'A valid argument was provided with an invalid value'
        self.info[USER_MESSAGE_KEY] = 'A valid argument was provided with an invalid value'
        self.info[CONTEXT_KEY] = context

        super(InvalidArgumentValue, self).__init__(self.info)


class ForbiddenBase(InfoException):
    """
    Inherit from this exception to create exceptions where the error is about forbidden.
    Error code for exceptions derived from this one should start with 403.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        super(ForbiddenBase, self).__init__(info)


class Forbidden(ForbiddenBase):
    """
    Use when a resource was tried to be accessed and the provided credentials
    do not include required permissions.
    Error code for exceptions derived from this one should start with 403.
    Use only when is not defined if the resource was tried to be read, written or executed.
    """

    def __init__(self, context):      # pylint: disable=E1002
        info = dict()
        info[DEVELOPER_MESSAGE_KEY] = 'Forbidden to access requested resource'
        info[USER_MESSAGE_KEY] = 'Forbidden to access requested resource'
        info[CONTEXT_KEY] = context

        super(Forbidden, self).__init__(info)


class UnauthorizedBase(InfoException):
    """
    Inherit from this exception to create exceptions where the error is about authorization.
    Error code for exceptions derived from this one should start with 401.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        super(UnauthorizedBase, self).__init__(info)


class Unauthorized(UnauthorizedBase):
    """
    Use when a resource was tried to be accessed and the provided credentials
    do not include required permissions.
    Error code for exceptions derived from this one should start with 401.
    Use only when is not defined if the resource was tried to be read, written or executed.
    """

    def __init__(self, context):      # pylint: disable=E1002
        info = dict()
        info[DEVELOPER_MESSAGE_KEY] = 'Unauthorized to access requested resource'
        info[USER_MESSAGE_KEY] = 'Unauthorized to access requested resource'
        info[CONTEXT_KEY] = context

        super(Unauthorized, self).__init__(info)


class UnauthorizedRead(UnauthorizedBase):
    """
    Use when a resource was tried to be read and the provided credentials
    do not include required permissions.
    """

    def __init__(self, context):      # pylint: disable=E1002
        info = dict()
        info[DEVELOPER_MESSAGE_KEY] = 'Unauthorized to read requested resource'
        info[USER_MESSAGE_KEY] = 'Unauthorized to read requested resource'
        info[CONTEXT_KEY] = context

        super(UnauthorizedRead, self).__init__(info)


class UnauthorizedWrite(UnauthorizedBase):
    """
    Use when a resource was tried to be written and the provided credentials
    do not include required permissions.
    """

    def __init__(self, context):      # pylint: disable=E1002
        info = dict()
        info[DEVELOPER_MESSAGE_KEY] = 'Unauthorized to write requested resource'
        info[USER_MESSAGE_KEY] = 'Unauthorized to write requested resource'
        info[CONTEXT_KEY] = context

        super(UnauthorizedWrite, self).__init__(info)


class UnauthorizedExecute(UnauthorizedBase):
    """
    Use when a resource was tried to be executed and the provided credentials
    do not include required permissions.
    """

    def __init__(self, context):      # pylint: disable=E1002
        info = dict()
        info[DEVELOPER_MESSAGE_KEY] = 'Unauthorized to execute requested resource'
        info[USER_MESSAGE_KEY] = 'Unauthorized to execute requested resource'
        info[CONTEXT_KEY] = context

        super(UnauthorizedExecute, self).__init__(info)


class NotFoundBase(InfoException):
    """
    Inherit from this exception to create exceptions where the error is about
    not found resources.
    Error code for exceptions derived from this one should start with 400.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        super(NotFoundBase, self).__init__(info)


class NotFound(NotFoundBase):
    """
    Use when an specific resource was requested and it was not found.
    Don't use in case of searches with no results.
    Context should include the resource that was not found, use ids or absolute paths whenever possible.
    """

    def __init__(self, context):      # pylint: disable=E1002
        info = dict()
        info[DEVELOPER_MESSAGE_KEY] = 'Resource not found'
        info[USER_MESSAGE_KEY] = 'Resource not found'
        info[CONTEXT_KEY] = context

        super(NotFound, self).__init__(info)


class MethodNotAllowedBase(InfoException):
    """
    Inherit from this exception to create exceptions where the error is about authorization.
    Error code for exceptions derived from this one should start with 401.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        super(MethodNotAllowedBase, self).__init__(info)


class MethodNotAllowed(MethodNotAllowedBase):
    """
    Use when an specific resource was requested and it was not found.
    Don't use in case of searches with no results.
    Context should include the resource that was not found, use ids or absolute paths whenever possible.
    """

    def __init__(self, context):      # pylint: disable=E1002
        info = dict()
        info[DEVELOPER_MESSAGE_KEY] = 'Method not allowed'
        info[USER_MESSAGE_KEY] = 'Method not allowed'
        info[CONTEXT_KEY] = context

        super(MethodNotAllowed, self).__init__(info)


class PermanentServiceError(InfoException):
    """
    Inherit from this exception if the error is a permanent service error that requires intervention
    to be solved.
    Error code for exceptions derived from this one should start with 500.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        super(PermanentServiceError, self).__init__(info)


class TemporaryServiceError(InfoException):
    """
    Inherit from this exception if the error is a temporary service error that may not cause other errors
    in subsequent requests.
    Error code for exceptions derived from this one should start with 503.
    Do not use this exception directly.
    """

    def __init__(self, info):                           # pylint: disable=E1002
        super(TemporaryServiceError, self).__init__(info)


class CouldNotConnectToDatabase(TemporaryServiceError):
    """
    Provider used in the request timed out or returned an error
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'Could not connect to database'
        self.info[USER_MESSAGE_KEY] = 'Could not connect to database'
        self.info[CONTEXT_KEY] = context

        super(CouldNotConnectToDatabase, self).__init__(self.info)


class DatabaseOperationError(TemporaryServiceError):
    """
    Use when a database operation failed but may be successful in subsequent requests.
    Context should include the operation that failed.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'Error while trying to read/write database'
        self.info[USER_MESSAGE_KEY] = 'Error while trying to read/write database'
        self.info[CONTEXT_KEY] = context

        super(DatabaseOperationError, self).__init__(self.info)


class ExternalProviderUnavailablePermanently(PermanentServiceError):
    """
    Use when a external service provider is not available.
    Context should include the operation that failed.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'An external provider is unavailable permanently'
        self.info[USER_MESSAGE_KEY] = 'An external provider is unavailable permanently'
        self.info[CONTEXT_KEY] = context

        super(ExternalProviderUnavailablePermanently, self).__init__(self.info)


class ExternalProviderUnavailableTemporarily(TemporaryServiceError):
    """
    Use when a external service provider is not available.
    Context should include the operation that failed.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = 'An external provider is unavailable temporarily'
        self.info[USER_MESSAGE_KEY] = 'An external provider is unavailable temporarily'
        self.info[CONTEXT_KEY] = context

        super(ExternalProviderUnavailableTemporarily, self).__init__(self.info)


class ExternalProviderBadResponse(PermanentServiceError):
    """
    Use when a external service provider response in a wrong way.
    Context should include the operation that failed.
    """

    def __init__(self, context):      # pylint: disable=E1002
        self.info = dict()
        self.info[DEVELOPER_MESSAGE_KEY] = "The external provider's response is not valid"
        self.info[USER_MESSAGE_KEY] = "The external provider's response is not valid"
        self.info[CONTEXT_KEY] = context

        super(ExternalProviderBadResponse, self).__init__(self.info)
