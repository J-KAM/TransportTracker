import os

from TransportTracker.execute.execute import execute
from TransportTracker.grammar.query import TicketQuery
from TransportTracker.settings import BASE_DIR


def main(example_file_name, debug=False):

    path = ""
    if BASE_DIR.__contains__('/'):
        path = BASE_DIR + "/TransportTracker"  # linux
    else:
        path = BASE_DIR + "\TransportTracker"  # windows

    model = execute(os.path.join(path, "grammar"), 'grammar.tx', example_file_name, debug, debug)

    query = TicketQuery()
    query.interpret(model)

if __name__ == '__main__':
    main('example.grammar', True)
    main('example1.grammar', True)
    main('example2.grammar', True)
    # main('example11.grammar', True)
    # main('example12.grammar', True)
    # main('example13.grammar', True)
    # main('example14.grammar', True)



