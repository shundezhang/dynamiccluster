from dynamiccluster.utilities import getLogger
from dynamiccluster.data import WorkerNode
from dynamiccluster.data import Instance
from dynamiccluster.exceptions import GraphiteReporterError
import threading
import time

log = getLogger(__name__)
info = None

class GraphiteReporter(threading.Thread):
    def __init__(self, _info=None, _resource=None, hostname="localhost", port=2003, interval=30, prefix="headnode.dynamiccluster"):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        global info
        info=_info
        self.__resource=_resource
        self.__running=True
        self.__address=(hostname, port)
        self.__interval=interval
        self.__prefix=prefix
        
    def run(self):
        global info
        import socket
        timeout_in_seconds = 2
        _socket = socket.socket()
        _socket.settimeout(timeout_in_seconds)
        try:
            _socket.connect(self.__address)
        except socket.timeout:
            raise GraphiteReporterError(
                "Took over %d second(s) to connect to %s" %
                (timeout_in_seconds, self.__address))
        except socket.gaierror:
            raise GraphiteReporterError(
                "No address associated with hostname %s:%s" % self.__address)
        except Exception as error:
            raise GraphiteReporterError(
                "unknown exception while connecting to %s - %s" %
                (self.__address, error)
            )
        log.debug("graphite reporter has started.")
        count=0
        while self.__running:
            if count%self.__interval==0:
                timestamp = int(time.time())
                wns = info.worker_nodes[:]
                
                wn_total=len(wns)
                wn_starting=len([wn for wn in wns if wn.state in [WorkerNode.Starting]])
                wn_deleting=len([wn for wn in wns if wn.state in [WorkerNode.Deleting]])
                wn_idle=len([wn for wn in wns if wn.state == WorkerNode.Idle])
                wn_busy=len([wn for wn in wns if wn.state == WorkerNode.Busy])
                wn_vacating=len([wn for wn in wns if wn.state in [WorkerNode.Holding, WorkerNode.Held]])
                wn_error=len([wn for wn in wns if wn.state in [WorkerNode.Error]])

                core_total=sum([wn.num_proc for wn in wns])
                core_starting=sum([wn.num_proc for wn in wns if wn.state in [WorkerNode.Starting]])
                core_deleting=sum([wn.num_proc for wn in wns if wn.state in [WorkerNode.Deleting]])
                core_idle=sum([wn.num_proc for wn in wns if wn.state == WorkerNode.Idle])
                core_busy=sum([wn.num_proc for wn in wns if wn.state == WorkerNode.Busy])
                core_vacating=sum([wn.num_proc for wn in wns if wn.state in [WorkerNode.Holding, WorkerNode.Held]])
                core_error=sum([wn.num_proc for wn in wns if wn.state in [WorkerNode.Error]])

                messages=[]
                messages.append("%s.%s %d %d" % (self.__prefix, "nodes.total",
                                          wn_total, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "nodes.starting",
                                          wn_starting, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "nodes.deleting",
                                          wn_deleting, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "nodes.busy",
                                          wn_busy, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "nodes.idle",
                                          wn_idle, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "nodes.vacating",
                                          wn_vacating, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "nodes.error",
                                          wn_error, timestamp))
                
                messages.append("%s.%s %d %d" % (self.__prefix, "cores.total",
                                          core_total, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "cores.starting",
                                          core_starting, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "cores.deleting",
                                          core_deleting, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "cores.busy",
                                          core_busy, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "cores.idle",
                                          core_idle, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "cores.vacating",
                                          core_vacating, timestamp))
                messages.append("%s.%s %d %d" % (self.__prefix, "cores.error",
                                          core_error, timestamp))
                
                for res, val in self.__resource.items():
                    messages.append("%s.%s %d %d" % (self.__prefix, "resource."+res+".nodes",
                                              len([wn for wn in wns if wn.instance and wn.instance.cloud_resource==res]), timestamp))
                    messages.append("%s.%s %d %d" % (self.__prefix, "resource."+res+".cores",
                                              sum([wn.num_proc for wn in wns if wn.instance and wn.instance.cloud_resource==res]), timestamp))

                messages.append("%s.%s %d %d" % (self.__prefix, "jobs.queued",
                                          info.total_queued_job_number, timestamp))
                del wns
                try:
                    _socket.sendall('\n'.join(messages)+'\n')
    
                # Capture missing socket.
                except socket.gaierror as error:
                    raise GraphiteReporterError(
                        "Failed to send data to %s, with error: %s" %
                        (self.__address, error))
        
                # Capture socket closure before send.
                except socket.error as error:
                    raise GraphiteReporterError(
                        "Socket closed before able to send data to %s, "
                        "with error: %s" %
                        (self.__address, error)
                    )
        
                except Exception as error:
                    raise GraphiteReporterError(
                        "Unknown error while trying to send data down socket to %s, "
                        "error: %s" %
                        (self.__address, error)
                    )
                count=0
            else:
                count+=1
            time.sleep(1)

        try:
            _socket.shutdown(1)

        # If its currently a socket, set it to None
        except AttributeError:
            _socket = None
        except Exception:
            _socket = None

        # Set the self.socket to None, no matter what.
        finally:
            _socket = None
        log.debug("graphite reporter has quit.")

    def stop(self):
        self.__running=False
