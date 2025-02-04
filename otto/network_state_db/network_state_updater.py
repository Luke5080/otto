import time
from threading import Thread
from otto.network_state_db.network_state import NetworkState
from deepdiff import DeepDiff

class NetworkStateUpdater(Thread):
    _nw_state: NetworkState

    def __init__(self):
        super().__init__()
        self._nw_state = NetworkState()

    def run(self):

        while True:
            print("Starting..")
            current_nw_state ={}
            for document in self._nw_state.get_network_state():
                current_nw_state[document["name"]] = document
            excluded_keys = [
            r"root\['[^']+'\]\['installedFlows'\]\['[^']+'\]\[\d+\]\['duration_nsec'\]",
            r"root\['[^']+'\]\['installedFlows'\]\['[^']+'\]\[\d+\]\['duration_sec'\]"
              ]
            print(DeepDiff(self._nw_state.get_registered_state(),current_nw_state,exclude_regex_paths=excluded_keys))

            time.sleep(60)
