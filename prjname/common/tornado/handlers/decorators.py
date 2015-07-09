import functools
from logging import getLogger
import time

from tornado import gen
from tornado import ioloop

from prjname.common import exceptions
from prjname.common import settings
from prjname.common.policy import configuration
from prjname.common.policy import enforcer
from prjname.common.policy import exceptions as policy_exceptions
from prjname.common.repositories.authorization.subscription_config import SubscriptionConfigRepository
from prjname.common.tokens import exceptions as token_exceptions
from prjname.common.tokens.jwt_token import JWTToken
from prjname.common.tornado.handlers.base import Context


# This decorator must be before @gen.coroutine
def oauth2_authorization(func=None):
    def the_decorator(func):
        @gen.coroutine
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                authorization_header = self.request.headers.get('Authorization')
                if not authorization_header:
                    raise exceptions.Unauthorized(
                        'Authorization header is missing')
                if 'Bearer ' not in authorization_header:
                    raise exceptions.Unauthorized(
                        'Invalid token type in Authorization HTTP header')

                try:
                    token_str = authorization_header[len('Bearer '):]
                    self.request.token = JWTToken(
                        token=token_str,
                        certificate=self.application_settings.PRIVATE_CERTIFICATE)
                    self.context = Context(self.request)
                    self.support.stat_set('active_families', self.context.account_id)
                    self.support.stat_set('active_devices', self.context.device_id)
                    logger = getLogger(settings.ANALYTICS_LOGGER_NAME)
                    extra = {
                        'env': self.mfs_environment,
                        'service': self.settings.get('service_name'),
                        'handler': self.handler,
                        'app': self.context.client_id,
                        'account': self.context.account_id,
                        'user': self.context.member_id,
                        'device': self.context.device_id
                    }
                    logger.info(None, extra=extra)
                except (TypeError, token_exceptions.InvalidToken):
                    raise exceptions.Unauthorized('Invalid token')

                if self.request.token.payload.get("client_id") is None:
                    raise exceptions.Unauthorized(
                        'Invalid token: missing client_id on payload.')

                if (self.application_settings.ENFORCE_POLICIES and
                        self.context.products):
                    configuration_policy = (
                        configuration.ConfigurationPolicy(
                            self.support, self.context))
                    policies_config = yield configuration_policy.get_policies(
                        self.context.products)

                    policy_enforcer = enforcer.Enforcer(policies_config)
                    try:
                        yield policy_enforcer.enforce(self.request, self)
                    except policy_exceptions.PolicyEnforcementFailed as ex:
                        raise exceptions.Forbidden(ex.message)

                yield func(self, *args, **kwargs)
            except exceptions.InfoException as ex:
                self.support.notify_error(ex)
                self.build_response(ex)
            except Exception as ex:  # pylint: disable=W0703
                self.support.notify_error(ex)
                self.build_response(ex)

        return wrapper

    if func:
        return the_decorator(func)
    else:
        return the_decorator


# This decorator must be before @gen.coroutine
def api_key_authorization(func=None, api_key_name='client_id', render_response=False):
    def the_decorator(func):
        @gen.coroutine
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                api_key_str = self.get_argument(api_key_name, default=False)

                if not api_key_str:
                    raise exceptions.Unauthorized('Missing api_key')

                subscription_config_repo = SubscriptionConfigRepository(
                    self.support,
                    self.settings.get('cassandra_adapter')
                )

                result = yield subscription_config_repo.get_subscription_from_client_id(api_key_str)
                if not result:
                    raise exceptions.Unauthorized('Invalid client_id query parameter.')

                self.context = Context(self.request)
                yield func(self, *args, **kwargs)
            except exceptions.InfoException as ex:
                self.support.notify_error(ex)
                if render_response:
                    formfactor = self.get_argument('formfactor', 'desktop')
                    templates_folder = settings.FORMFACTOR_TO_TEMPLATES_FOLDER[formfactor]
                    form_doc = "{0}/{1}".format(templates_folder, "internal_error.html")
                    self.render(form_doc,
                                error_message=ex.message)
                else:
                    self.build_response(ex)
            except Exception as ex:  # pylint: disable=W0703
                self.support.notify_error(ex)
                self.build_response(ex)

        return wrapper

    if func:
        return the_decorator(func)
    else:
        return the_decorator


def retry(exception_to_check, tries=3, delay=3, backoff=2, support=None):  # pylint: disable=unused-argument
    """
    Retry calling the decorated function using an exponential backoff

    @param exception_to_check: may be one exception or a tuple of them
    @param tries: number of times to try
    @param delay: initial delay between retries in seconds
    @param backoff: backoff multiplier. E.g. value of 2 will double the delay after each retry
    """

    def decorator_retry(function):
        """
        Decorator to retry function calls using an exponential backoff
        @param function function to decorate
        """

        @gen.coroutine
        @functools.wraps(function)
        def function_retry(*args, **kwargs):
            """
            Retry algorithm using an exponential backoff
            """

            number_of_tries = tries
            delay_seconds = delay

            while number_of_tries > 1:
                try:
                    response = yield function(*args, **kwargs)
                    raise gen.Return(response)
                except exception_to_check:
                    yield gen.Task(ioloop.IOLoop.current().add_timeout,
                                   time.time() + delay_seconds)
                    number_of_tries -= 1
                    delay_seconds *= backoff

            response = yield function(*args, **kwargs)
            raise gen.Return(response)

        return function_retry   # Decorator

    return decorator_retry
