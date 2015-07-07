import cassandra
from cassandra import cluster
from cassandra.io import libevreactor
from tornado import concurrent

from prjname.common import exceptions


ConsistencyLevel = cassandra.ConsistencyLevel


class CassandraAdapter(object):  # pylint: disable=R0903
    INSTANCE = {}

    def __init__(self, *args, **kwargs):
        self.setting = kwargs
        kwargs["connection_class"] = libevreactor.LibevConnection
        cluster.Session.default_fetch_size = None
        self.cluster = cluster.Cluster(*args, **kwargs)

    def connect(self, keyspace):
        if keyspace not in self.INSTANCE:
            self.INSTANCE[keyspace] = self.cluster.connect(keyspace)
        return self.INSTANCE[keyspace]

    def execute_async(self, keyspace, query, params=None,
                      consistency_level=cassandra.ConsistencyLevel.QUORUM):
        statement = cassandra.query.SimpleStatement(
            query, consistency_level=consistency_level)
        cassandra_future = self.connect(keyspace).execute_async(
            statement, params or {})
        return self.to_tornado_future(cassandra_future)

    @staticmethod
    def to_tornado_future(cassandra_future):
        tornado_future = concurrent.Future()

        def callback_success(result):
            tornado_future.set_result(result)

        def callback_error(ex):
            tornado_future.set_exception(
                exceptions.DatabaseOperationError(ex.message))

        cassandra_future.add_callbacks(callback_success, callback_error)
        return tornado_future
