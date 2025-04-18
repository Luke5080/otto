class SwitchRetrievalException(Exception):
    pass


class PortRetrievalException(Exception):
    pass


class PortMappingException(Exception):
    pass


class HostRetrievalException(Exception):
    pass


class FlowRetrievalException(Exception):
    pass


class NetworkDatabaseException(Exception):
    pass


class SwitchDocumentNotFound(Exception):
    pass


class MultipleNetworkDbOperators(Exception):
    pass


class MultipleNetworkStateInstances(Exception):
    pass

class ProcessedIntentsDbException(Exception):
    pass

class MultipleFlaskApiException(Exception):
    pass

class MultipleGunicornManager(Exception):
    pass

class AuthenticationError(Exception):
    pass

class ApiRequestError(Exception):
    pass