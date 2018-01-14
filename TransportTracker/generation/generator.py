import os

from TransportTracker.execute.execute import execute
from TransportTracker.settings import BASE_DIR


def main(example_file_name,debug=False):
    path = BASE_DIR + "\TransportTracker"
    model = execute(os.path.join(path, "grammar"), 'grammar.tx', example_file_name, debug, debug)


if __name__ == '__main__':
    main('example.grammar', True)
    main('example1.grammar', True)
    main('example2.grammar', True)
    #main('example14.grammar', True)
