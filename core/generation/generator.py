import os
import datetime

from jinja2 import Environment, PackageLoader

from TransportTracker.execute.execute import execute
from TransportTracker.grammar.query import TicketQuery
from TransportTracker.settings import BASE_DIR
from root import root


def generate(template_name, output_name, render_vars):

    env = Environment(trim_blocks=True, lstrip_blocks=True, loader=PackageLoader("core", "generation/templates"))
    env.filters['flight_type'] = flight_type
    env.filters['departure'] = departure
    env.filters['arrival'] = arrival
    template = env.get_template(template_name)
    rendered = template.render(render_vars)

    file_path = ""
    if BASE_DIR.__contains__('/'):
        file_path = "core/templates/core"  # linux
    else:
        file_path = "core\\templates\core"  # windows

    file_name = os.path.join(root, file_path, output_name)
    with open(file_name, "w+") as f:
        f.write(rendered)


def flight_type(flights):
    if len(flights) > 1:
        return "transfer"
    else:
        return "direct"


def departure(flights):
    date_time = flights[0]['departs_at']
    date = datetime.datetime.strptime(date_time.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    time = date_time.split('T')[1]
    return "on " + date + " at " + time


def arrival(flights):
    date_time = flights[-1]['arrives_at']
    date = datetime.datetime.strptime(date_time.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    time = date_time.split('T')[1]
    return "on " + date + " at " + time


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



