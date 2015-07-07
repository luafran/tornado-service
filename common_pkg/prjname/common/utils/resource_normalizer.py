"""
Resource normalizer
"""
from collections import namedtuple

from prjname.common import exceptions
import collections


RULE_NT = namedtuple('Rule', ['execute', 'args', 'default'])


def Rule(args, execute=None, default=None):                             # pylint: disable=C0103
    """
    Returns a named tuple that represent a transformation rule
    @param args set of arguments to be used by the rule
    @param execute transformation function who receive the args
    @param default value used when the attribute defined by path is not in the resource
    """

    return RULE_NT(execute, args, default)


def normalize_resources(resources, normalization_rules, is_ordered=False):
    """
    Normalize a list of resources based on a set of rules
    @param resources list of resources to be normalized
    @param normalization_rules set of rules to normalize the resources
    @param is_ordered mantain the order specified in the schema
    """

    normalized_resources = []
    for resource in resources:
        normalized_resource = normalize_resource(resource,
                                                 normalization_rules,
                                                 is_ordered)
        normalized_resources.append(normalized_resource)

    return normalized_resources


def normalize_resource(resource, normalization_rules, is_ordered=False):
    """
    Normalize a resource based on a set of rules
    @param resources list of resources to be normalized
    @param normalization_rules set of rules to normalize the resources
    @param is_ordered mantain the order specified in the schema
    """

    normalized_resource = {}

    for resource_path, rule in normalization_rules.iteritems():
        if isinstance(rule, dict):
            normalized_value = normalize_resource(resource,
                                                  rule,
                                                  is_ordered)
        else:
            normalized_value = _normalize(rule, resource)

        _set_resource_value_based_on_dotted_path(resource_path,
                                                 normalized_value,
                                                 normalized_resource)

    return normalized_resource


def normalize_response(response, normalization_rules=None):
    """
    Normalize the external service response using the normalization rules
    """
    # pylint: disable=R0201
    normalizer_mapping = {
        dict: normalize_resource,
        list: normalize_resources,
        collections.OrderedDict: normalize_resource
    }

    if normalization_rules is None:
        return response

    try:
        normalized_response = normalizer_mapping[type(response)](
            response, normalization_rules)
    except KeyError as ex:
        raise ValueError('Normalization error: %s' % ex)

    return normalized_response


# Helper method


def _normalize(rule, resource):
    """
    Apply a transformation rule to the resource
    @param rule transformation rule to be applied to the resource
    @param resource resource to transform
    """

    execute = rule.execute
    args = rule.args
    default = rule.default

    kwargs = {}
    for arg in args:
        kwargs[arg.split('.')[-1]] = _get_resource_value_based_on_dotted_path(
            arg, resource, default if not execute else None)

    if execute:
        try:
            normalized_value = execute(**kwargs)
        except Exception:  # pylint: disable=W0703
            normalized_value = default
    elif len(kwargs) > 1:
        raise exceptions.InvalidArgument(
            'too many args for a rule with no "execute"')
    else:
        normalized_key, normalized_value = kwargs.popitem()  # pylint: disable=W0612

    return normalized_value


def _set_resource_value_based_on_dotted_path(path, value, resource):  # pylint: disable=C0103
    """
    Set a resource value based on a dotted path
    @param path string containing a dotted path to an attribute
    @param value value to be set to the attribute specified by path
    @param resource resource who contains the attribute to be changed
    """

    splitted_path = path.split('.')

    for index, path_key in enumerate(splitted_path):
        if index == len(splitted_path) - 1:
            resource[path_key] = value
        else:
            resource = resource[path_key]


def _get_resource_value_based_on_dotted_path(path, resource, default):  # pylint: disable=C0103
    """
    Get a resource value based on a dotted path
    @param path string containing a dotted path to an attribute
    @param resource resource who contains the attribute to be returned
    @param default value used when the attribute defined by path is not in the resource
    """

    splitted_path = path.split('.')

    try:
        for path_key in splitted_path:
            resource = resource.get(path_key, default)
    except AttributeError:
        pass

    return resource
