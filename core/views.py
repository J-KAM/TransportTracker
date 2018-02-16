import requests
from django.shortcuts import render, render_to_response
from django.views import View

from TransportTracker.grammar.query import TicketQuery
from core.forms import QueryForm

from textx.exceptions import TextXSyntaxError, TextXSemanticError
import os
from TransportTracker.settings import BASE_DIR
from TransportTracker.execute.execute import execute_for_web
from core.generation.generator import generate
from core.models import City


class QueryFormView(View):
    form_class = QueryForm
    template_name = 'core/index.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form, 'error_message': ''})

    def post(self, request):
        form = self.form_class(request.POST)

        query = request.POST['query'].lower()
        query = " ".join(query.splitlines())

        path = ""
        if BASE_DIR.__contains__('/'):
            path = BASE_DIR + "/TransportTracker"  # linux
        else:
            path = BASE_DIR + "\TransportTracker"  # windows

        try:
            model = execute_for_web(os.path.join(path, "grammar"), 'grammar.tx', query, True, True)
            query = TicketQuery()
            query.interpret(model)

            departure_city_code = ""
            arrival_city_code = ""

            if City.objects.filter(name=model.From.departure_city).exists():
                departure_city_code = City.objects.get(name=model.From.departure_city).iata_code
            if City.objects.filter(name=model.to.arrival_city).exists():
                arrival_city_code = City.objects.get(name=model.to.arrival_city).iata_code

            flights_url = ""

            if model.ticket_type.type == 'round-trip':
                if model.price is not None:
                    flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                                  '&destination=' + arrival_city_code + \
                                  '&departure_date=' + model.on.departure_date + \
                                  '&return_date=' + model.return_date.return_date + \
                                  '&adults=' + model.number_of_tickets.number +\
                                  '&max_price=' + model.price.price + \
                                  '&currency=' + model.currency.currency
                else:
                    flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                                  '&destination=' + arrival_city_code + \
                                  '&departure_date=' + model.on.departure_date + \
                                  '&return_date=' + model.return_date.return_date + \
                                  '&adults=' + model.number_of_tickets.number
            else:
                if model.price is not None:
                    flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                                  '&destination=' + arrival_city_code + \
                                  '&departure_date=' + model.on.departure_date + \
                                  '&adults=' + model.number_of_tickets.number +\
                                  '&max_price=' + model.price.price + \
                                  '&currency=' + model.currency.currency
                else:
                    flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                                  '&destination=' + arrival_city_code + \
                                  '&departure_date=' + model.on.departure_date + \
                                  '&adults=' + model.number_of_tickets.number

            if flights_url != "":
                flights_response = requests.get(flights_url).json()
                filtered_flights = []
                if 'results' in flights_response:
                    for flight in flights_response['results']:
                        if model.ticket_class.Class in flight['travel_class'].lower():
                            filtered_flights.append(flight)

                generate("results_template.html", "results.html", {"filtered_flights": filtered_flights,
                                                                    "from": model.From.departure_city,
                                                                    "to": model.to.arrival_city})

        except TextXSyntaxError as error:
            return render(request, self.template_name, {'form': form, 'error_message': syntax_error_message(str(error))})
        except TextXSemanticError as error:
            return render(request, self.template_name, {'form': form, 'error_message': error})

        return render(request, 'core/results.html')


def syntax_error_message(error):
    if error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|one-way\s|round-trip\s))'"):
        return "You didn't define number of tickets or ticket type (one-way or round-trip)."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|economy\s|business\s|first\s|second\s|couchette\s))'"):
        return "You must define ticket class."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|plane\s|bus\s|train\s))'"):
        return "You must define mean of transport (plane, train or bus)."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|[1-9]\d*\s))'"):
        return "You must define number of tickets."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|from\s))'"):
        return "You must define departure city."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|to\s))'"):
        return "You must define arrival city."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|on\s))'"):
        return "You must define departure date."
    elif error.startswith("Expected '0[1-9]' or '[1-2][0-9]' or '3[0-1]'"):
        return "Date isn't valid. Expected date format is DD.MM.YYYY or DD/MM/YYYY."
    elif error.startswith("Expected '0[1-9]' or '1[0-2]'"):
        return "Date isn't valid. Expected date format is DD.MM.YYYY or DD/MM/YYYY."
    elif error.startswith("Expected Year"):
        return "Date isn't valid. Expected date format is DD.MM.YYYY or DD/MM/YYYY."
    elif error.startswith("Expected '/' or '.'"):
        return "Date isn't valid. Expected date format is DD.MM.YYYY or DD/MM/YYYY."

