import logging
import signal

from bubuku.broker import BrokerManager
from bubuku.controller import Controller, Change

_LOG = logging.getLogger('bubuku.features.terminate')


class StopBrokerChange(Change):
    def __init__(self, broker: BrokerManager):
        self.broker = broker

    def get_name(self):
        return 'stop'

    def can_run(self, current_actions):
        return all([action not in current_actions for action in ['start', 'restart', 'stop']])

    def run(self, current_actions):
        _LOG.info('Stopping kafka process')
        self.broker.stop_kafka_process()

    def can_run_at_exit(self):
        return True


__REGISTERED = None


def get_registration():
    if not __REGISTERED:
        return None, None
    return __REGISTERED


def register_terminate_on_interrupt(controller: Controller, broker: BrokerManager):
    global __REGISTERED
    if __REGISTERED:
        return

    def _sig_handler(*args, **kwargs):
        _LOG.info('Signal was caught, stopping controller gracefully')
        controller.stop(StopBrokerChange(broker))

    _LOG.info('Registering signal handler')
    signal.signal(signal.SIGTERM, _sig_handler)
    __REGISTERED = (controller, broker)
