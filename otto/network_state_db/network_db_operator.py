from pymongo import MongoClient
from exceptions import NetworkDatabaseException, SwitchDocumentNotFound
from pymongo.errors import PyMongoError

class NetworkDbOperator:
    _MongoConnector : MongoClient

    def __init__(self):
        self._MongoConnector = MongoClient('localhost', 27017)
        self._network_state_db = self._MongoConnector["topology"]
        self._switch_collection = self._network_state_db["switches"]

    def put_switch_to_db(self, switch_struct: dict) -> None:
        try:
            self._switch_collection.insert_one(switch_struct)

        except PyMongoError as e:
            raise NetworkDatabaseException(
                f"""
                Exception occurred while attempting to put a document into MongoDB.
                Exception raised: {e}
                """
            )

        except Exception as e:
            raise NetworkDatabaseException(e)

    def modify_switch_document(self, switch_dpid: str, **kwargs) -> None:

        match_exp = { 'name' : switch_dpid }

        try:
            self._switch_collection.update_one(match_exp, kwargs)
        except PyMongoError as e:
            raise NetworkDatabaseException(
                f"""
                    Exception occurred while attempting to modify a document for {switch_dpid}.
                    Exception raised: {e}
                    """
            )

    def remove_switch_document(self, switch_dpid: str) -> None:

        try:
            self._switch_collection.delete_one({"name" : switch_dpid})
        except PyMongoError as e:
            raise NetworkDatabaseException(
                f"""
                Exception occurred while attempting to remove a document in MongoDB.
                Exception raised: {e}
                """
            )

        except Exception as e:
            raise NetworkDatabaseException(e)

    def get_switch_document(self, switch_dpid: str):
        try:
            switch_entry = self._switch_collection.find_one({'name': switch_dpid})
        except PyMongoError as e:
            raise NetworkDatabaseException(
                f"""
                Exception occurred while attempting to retrieve a document in MongoDB.
                Exception raised: {e}
                """
            )

        if switch_entry is None:
            raise SwitchDocumentNotFound

    def dump_network_db(self):
        dumped_db = []
        for collection in self._switch_collection.find():
            del collection["_id"]
            dumped_db.append(collection)

        return dumped_db
