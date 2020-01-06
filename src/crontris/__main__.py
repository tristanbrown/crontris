"""Main module for running scheduler."""
import crontris
from .messaging import Listener

def run():
    """Main method to run the app."""
    crontris.scheduler.start()
    Listener().start()

if __name__ == "__main__":
    run()
