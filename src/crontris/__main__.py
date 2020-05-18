"""Main module for running scheduler."""
import crontris
from .messaging import Listener

def run():
    """Main method to run the app.

    Initializes a blank scheduler and the rabbitmq listener in separate threads. 
    """
    crontris.scheduler.start()
    Listener().start()

if __name__ == "__main__":
    run()
