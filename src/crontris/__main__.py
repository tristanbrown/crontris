"""Main module for running scheduler."""
from crontris import scheduler
from .messaging import Listener

def run():
    """Main method to run the app."""
    scheduler.start()
    Listener().start()

if __name__ == "__main__":
    run()
