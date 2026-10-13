from shared.worker import run
from .handler import NotificationsHandler

if __name__ == '__main__':
    run(NotificationsHandler, 'notifications')
