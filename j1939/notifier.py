import threading
try:
    import queue
except ImportError:
    import Queue as queue
    
from can import CanError
from can.notifier import Notifier as canNotifier
import socket

#same as a CAN Notifier but will listen to a queue
#recv function.

class Notifier(object):

    def __init__(self, queue, listeners, timeout=None):
        """Manages the distribution of **Messages** from a given bus to a list of listeners.

        :param bus: The :ref:`bus` to listen too.
        :param listeners: An iterable of :class:`~can.Listeners`
        :param timeout: An optional maximum number of seconds to wait for any message.
        """
        self.listeners = listeners
        self.queue = queue
        self.timeout = timeout

        self.running = threading.Event()
        self.running.set()

        self._reader = threading.Thread(target=self.rx_thread)
        self._reader.daemon = True

        self._reader.start()

    def stop(self):
        """Stop notifying Listeners when new :class:`~can.Message` objects arrive
         and call :meth:`~can.Listener.stop` on each Listener."""
        self.running.clear()
        if self.timeout is not None:
            self._reader.join(self.timeout + 0.1)

    def rx_thread(self):
        while self.running.is_set():
            msg = self.queue.get(timeout=self.timeout)
            if msg is not None:
                for callback in self.listeners:
                    callback(msg)

        for listener in self.listeners:
            listener.stop()

class CanNotifier(canNotifier):
    def _rx_thread(self, bus):
        msg = None
        try:
            while self._running:
                if msg is not None:
                    with self._lock:
                        for callback in self.listeners:
                            callback(msg)
                msg = bus.recv(self.timeout)

        # 
        # The next two handlers are intended to mask race conditions that can occur when 
        # we are blocked on a can-receive and close the bus.
        except CanError as err:
            if self._running:
                raise
        except ValueError as err:
            if self._running:
                raise
                
        except Exception as exc:
            self.exception = exc
            raise    
