class NoClusterDefinedException(Exception):
    pass

class ServerInitializationError(Exception):
    pass

class NoCloudResourceException(Exception):
    pass

class WorkerNodeNotFoundException(Exception):
    pass

class DuplicatedWorkerNodeException(Exception):
    pass

class CloudResourceNotFoundException(Exception):
    pass

class InvalidStateException(Exception):
    pass

class DuplicatedCloudResourceException(Exception):
    pass

class CloudNotAvailableException(Exception):
    pass

class FlavorNotFoundException(Exception):
    pass

class CloudNotSupportedException(Exception):
    pass

class ConfigCheckerNotSupportedException(Exception):
    pass

class ConfigCheckerError(Exception):
    pass

class PluginInitialisationError(Exception):
    pass

class GraphiteReporterError(Exception):
    pass

class InsufficientResourceException(Exception):
    pass