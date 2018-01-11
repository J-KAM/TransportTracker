import os

from TransportTracker.execute.execute import execute
from TransportTracker.settings import BASE_DIR


def main(debug=False):
    path = BASE_DIR + "\TransportTracker"
    model = execute(os.path.join(path, "grammar"), 'grammar.tx', 'example.grammar', debug, debug)


if __name__ == '__main__':
    main(True)