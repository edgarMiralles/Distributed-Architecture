from typing import Union, Dict
import grpc
import logging
from KVStore.protos.kv_store_pb2 import GetRequest, PutRequest, GetResponse, AppendRequest
from KVStore.protos.kv_store_pb2_grpc import KVStoreStub
from KVStore.protos.kv_store_shardmaster_pb2 import QueryRequest, QueryResponse, QueryReplicaRequest, Operation
from KVStore.protos.kv_store_shardmaster_pb2_grpc import ShardMasterStub

logger = logging.getLogger(__name__)


def _get_return(ret: GetResponse) -> Union[str, None]:
    if ret.HasField("value"):
        return ret.value
    else:
        return None


class SimpleClient:
    def __init__(self, kvstore_address: str):
        self.channel = grpc.insecure_channel(kvstore_address)
        self.stub = KVStoreStub(self.channel)

    def get(self, key: int) -> Union[str, None]:
        return _get_return(
            self.stub.Get(
                GetRequest(
                    key=key
                )
            )
        )

    def l_pop(self, key: int) -> Union[str, None]:
        return _get_return(
            self.stub.LPop(
                GetRequest(
                    key=key
                )
            )
        )

    def r_pop(self, key: int) -> Union[str, None]:
        return _get_return(
            self.stub.RPop(
                GetRequest(
                    key=key
                )
            )
        )

    def put(self, key: int, value: str):
        self.stub.Put(
            PutRequest(
                key=key,
                value=value
            )
        )

    def append(self, key: int, value: str):
        self.stub.Append(
            AppendRequest(
                key=key,
                value=value
            )
        )

    def stop(self):
        self.channel.close()


class ShardClient(SimpleClient):
    def __init__(self, shard_master_address: str):
        self.channel = grpc.insecure_channel(shard_master_address)
        self.stub = ShardMasterStub(self.channel)

    def get(self, key: int) -> Union[str, None]:
        queryResponse = self.stub.Query(QueryRequest(key=key))
        kvChannel = grpc.insecure_channel(queryResponse.server)
        kvStub = KVStoreStub(kvChannel)
        return _get_return(kvStub.Get(GetRequest(key=key)))

    def l_pop(self, key: int) -> Union[str, None]:
        queryResponse = self.stub.Query(QueryRequest(key=key))
        kvChannel = grpc.insecure_channel(queryResponse.server)
        kvStub = KVStoreStub(kvChannel)
        return _get_return(kvStub.LPop(GetRequest(key=key)))

    def r_pop(self, key: int) -> Union[str, None]:
        queryResponse = self.stub.Query(QueryRequest(key=key))
        kvChannel = grpc.insecure_channel(queryResponse.server)
        kvStub = KVStoreStub(kvChannel)
        return _get_return(kvStub.RPop(GetRequest(key=key)))

    def put(self, key: int, value: str):
        queryResponse = self.stub.Query(QueryRequest(key=key))
        kvChannel = grpc.insecure_channel(queryResponse.server)
        kvStub = KVStoreStub(kvChannel)
        kvStub.Put(PutRequest(
            key=key,
            value=value
        ))

    def append(self, key: int, value: str):
        queryResponse = self.stub.Query(QueryRequest(key=key))
        kvChannel = grpc.insecure_channel(queryResponse.server)
        kvStub = KVStoreStub(kvChannel)
        kvStub.Append(AppendRequest(
            key=key,
            value=value
        ))


class ShardReplicaClient(ShardClient):

    def get(self, key: int) -> Union[str, None]:
        response = self.stub.QueryReplica(
            QueryReplicaRequest(
                key=key,
                operation=Operation.Value("GET")
            )
        )
        kvChannel = grpc.insecure_channel(response.server)
        kvStub = KVStoreStub(kvChannel)
        return _get_return(kvStub.Get(GetRequest(key=key)))

    def l_pop(self, key: int) -> Union[str, None]:
        response = self.stub.QueryReplica(
            QueryReplicaRequest(
                key=key,
                operation=Operation.Value("L_POP")
            )
        )
        kvChannel = grpc.insecure_channel(response.server)
        kvStub = KVStoreStub(kvChannel)
        return _get_return(kvStub.LPop(GetRequest(key=key)))

    def r_pop(self, key: int) -> Union[str, None]:
        response = self.stub.QueryReplica(
            QueryReplicaRequest(
                key=key,
                operation=Operation.Value("R_POP")
            )
        )
        kvChannel = grpc.insecure_channel(response.server)
        kvStub = KVStoreStub(kvChannel)
        return _get_return(kvStub.RPop(GetRequest(key=key)))

    def put(self, key: int, value: str):
        response = self.stub.QueryReplica(
            QueryReplicaRequest(
                key=key,
                operation=Operation.Value("PUT")
            )
        )
        kvChannel = grpc.insecure_channel(response.server)
        kvStub = KVStoreStub(kvChannel)
        kvStub.Put(PutRequest(
            key=key,
            value=value
        ))

    def append(self, key: int, value: str):
        response = self.stub.QueryReplica(
            QueryReplicaRequest(
                key=key,
                operation=Operation.Value("APPEND")
            )
        )
        kvChannel = grpc.insecure_channel(response.server)
        kvStub = KVStoreStub(kvChannel)
        kvStub.Append(AppendRequest(
            key=key,
            value=value,
        ))
