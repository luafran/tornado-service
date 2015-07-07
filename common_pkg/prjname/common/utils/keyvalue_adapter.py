'''
Adapter to key value database
'''
import json
import re
import sys

from tornado import gen
import stevedore

from prjname.common import exceptions
from prjname.common import settings
from prjname.common.utils import cassandra_adapter


EXTENSIONS = stevedore.extension.ExtensionManager(
    namespace='prjname.common.repositories.views')


class KeyValueAdapter(object):  # pylint: disable=R0201,R0903
    """
    Adapter to KeyValue database
    """

    LOG_TAG = '[KeyValue Adapter] %s'

    def __init__(self,
                 cb_bucket='default',
                 hosts=settings.CASSANDRA_HOSTS,
                 keyspace='system',
                 auth_provider=None):

        self._bucket = cb_bucket
        self._keyspace = keyspace
        self._support = None

        try:
            self._adapter = cassandra_adapter.CassandraAdapter(
                contact_points=hosts,
                port=settings.CASSANDRA_PORT,
                auth_provider=auth_provider
            )

            self._session = self._adapter.connect(keyspace)
        except Exception as ex:
            raise exceptions.CouldNotConnectToDatabase("Could not connect to Cassandra: %s" % ex.message)

    def set_support(self, support):
        self._support = support

    @gen.coroutine
    def get(self, key):
        data = yield self._get_internal(key)
        raise gen.Return(data)

    @gen.coroutine
    def multi_get(self, keys):
        data = yield self._multi_get_internal(keys)
        raise gen.Return(data)

    @gen.coroutine
    def get_all(self):
        data = yield self._multi_get_internal()
        raise gen.Return(data)

    @gen.coroutine
    def get_value(self, key):
        """
        Retrieve from db the value associated with key
        @param key: the key to get the value for
        """
        data = yield self._get_internal(key)
        raise gen.Return(data.get("value"))

    @gen.coroutine
    def get_all_values(self):
        data = yield self._multi_get_internal()
        raise gen.Return([each_datum.get("value") for each_datum in data])

    @gen.coroutine
    def multi_get_values(self, keys):
        data = yield self._multi_get_internal(keys)
        raise gen.Return([each_datum.get("value") for each_datum in data])

    @gen.coroutine
    def add_value(self, key, value):
        try:
            key_found = yield self._get_internal(key)
        except exceptions.DatabaseOperationError:
            key_found = None
        if not key_found:
            yield self._insert_internal(key, value)
        else:
            raise exceptions.DatabaseOperationError('Invalid Key %s, it already exists' % key)
        raise gen.Return(key)

    @gen.coroutine
    def set_value(self, key, value, ttl=0):
        """
        Sets the value for the key in the db
        @param key: the key to set the value for
        @param value: the value to set
        @param ttl: If specified, the key will expire after specified seconds. Default value 0 does not expire
        """
        try:
            key_found = yield self._get_internal(key)
        except exceptions.DatabaseOperationError:
            key_found = None
        if key_found:
            yield self._update_internal(key, value, ttl)
        else:
            yield self._insert_internal(key, value, ttl)
        raise gen.Return(key)

    @gen.coroutine
    def delete_key(self, key):
        """
        Retrieve from db the value associated with key
        @param key: the key to get the value for
        """
        yield self._get_internal(key)
        result = yield self._delete_internal(key)
        raise gen.Return(result)

    @gen.coroutine
    def query(self, **kwargs):
        result = yield self._execute_extensions_on_get(kwargs)
        raise gen.Return(result)

    @gen.coroutine
    def _get_internal(self, key):
        criteria = {
            "table": self._bucket,
            "key": key
        }
        result = yield self._adapter.execute_async(
            self._keyspace,
            """
            SELECT *
              FROM {table}
             WHERE key = %(key)s
            """.format(**criteria),
            criteria)

        data = None
        for row in result:
            data = {
                "key": row.key,
                "value": json.loads(row.value)
            }
        if data is None:
            raise exceptions.DatabaseOperationError('Value for Key %s on table %s not found' %
                                                    (criteria.get("table"), criteria.get("key")))

        if self._support:
            self._support.stat_increment('db.total_count')
            self._support.stat_increment('db.get_count')
            self._support.stat_increment('db.get_bytes', sys.getsizeof(data))

        raise gen.Return(data)

    @gen.coroutine
    def _multi_get_internal(self, keys=None):
        criteria = {
            "table": self._bucket,
            "keys": ""
        }
        if keys is not None:
            criteria['keys'] = "WHERE key in ('{0}')".format("', '".join(keys))

        result = yield self._adapter.execute_async(
            self._keyspace,
            """
            SELECT *
              FROM {table}
              {keys}
            """.format(**criteria),
            criteria)

        rows = []
        for row in result:
            data = {
                "key": row.key,
                "value": json.loads(row.value)
            }
            rows.append(data)

        if self._support:
            self._support.stat_increment('db.total_count')
            self._support.stat_increment('db.get_count')
            self._support.stat_increment('db.get_bytes', sys.getsizeof(rows))

        raise gen.Return(rows)

    @gen.coroutine
    def _insert_internal(self, key, value, ttl=0):
        data = {
            "table": self._bucket,
            "key": key,
            "value": json.dumps(value),
            "ttl": ttl
        }

        yield self._adapter.execute_async(
            self._keyspace,
            """
            INSERT INTO {table} (key,
                                 value)
                 VALUES (%(key)s,
                         %(value)s)
                 USING TTL {ttl}
            """.format(**data),
            data)

        yield self._execute_extensions_on_set(key, value)

        if self._support:
            self._support.stat_increment('db.total_count')
            self._support.stat_increment('db.insert_count')
            insert_bytes = sys.getsizeof(key) + sys.getsizeof(value)
            self._support.stat_increment('db.insert_bytes', insert_bytes)

        raise gen.Return()

    @gen.coroutine
    def _update_internal(self, key, value, ttl):
        data = {
            "table": self._bucket,
            "key": key,
            "value": json.dumps(value),
            "ttl": ttl
        }
        yield self._adapter.execute_async(
            self._keyspace,
            """
            UPDATE {table} USING TTL {ttl}
               SET value = %(value)s
             WHERE key = %(key)s
            """.format(**data),
            data)

        yield self._execute_extensions_on_delete(key)
        yield self._execute_extensions_on_set(key, value)

        if self._support:
            self._support.stat_increment('db.total_count')
            self._support.stat_increment('db.update_count')
            self._support.stat_increment('db.update_bytes', sys.getsizeof(value))

        raise gen.Return()

    @gen.coroutine
    def _delete_internal(self, key):
        data = {
            "table": self._bucket,
            "key": key
        }
        yield self._adapter.execute_async(
            self._keyspace,
            """
            DELETE FROM {table}
             WHERE key = %(key)s
            """.format(**data),
            data)

        yield self._execute_extensions_on_delete(key)

        if self._support:
            self._support.stat_increment('db.total_count')
            self._support.stat_increment('db.delete_count')

        raise gen.Return(True)

    @gen.coroutine
    def _execute_extensions_on_set(self, key, value):
        extensions = get_extensions(self._bucket)

        for extension in extensions:
            instance = extension.plugin(None,
                                        None,
                                        None,
                                        self._adapter,
                                        self._keyspace)
            yield instance.on_set(key, value)

    @gen.coroutine
    def _execute_extensions_on_get(self, criteria):
        result = []
        extensions = get_extensions(self._bucket)

        for extension in extensions:
            instance = extension.plugin(None,
                                        None,
                                        None,
                                        self._adapter,
                                        self._keyspace)
            rows = yield instance.on_get(criteria)
            result.extend(rows)
        raise gen.Return(result)

    @gen.coroutine
    def _execute_extensions_on_delete(self, key):
        extensions = get_extensions(self._bucket)

        for extension in extensions:
            instance = extension.plugin(None,
                                        None,
                                        None,
                                        self._adapter,
                                        self._keyspace)
            yield instance.on_delete(key)


def get_extensions(bucket):
    pattern = re.compile("{0}+".format(bucket))
    extensions = []

    for extension in EXTENSIONS:
        if pattern.match(extension.name):
            extensions.append(extension)
    return extensions
