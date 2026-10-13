from shared.worker import run
from .handler import BillingHandler

if __name__ == '__main__':
    run(BillingHandler, 'billing')
