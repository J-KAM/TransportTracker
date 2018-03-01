import requests
from django.shortcuts import render
from django.views import View

from TransportTracker.grammar.query import TicketQuery
from core.forms import QueryForm

from textx.exceptions import TextXSyntaxError, TextXSemanticError
import os
from TransportTracker.settings import BASE_DIR
from TransportTracker.execute.execute import execute_for_web
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
            url = ""

            if model.transport_type.transport == 'plane':
                url = create_flight_url(model)

                if url != "":
                    flights_response = requests.get(url).json()
                    filtered_flights = []
                    if 'results' in flights_response:
                        for flight in flights_response['results']:
                            if model.ticket_class.Class in flight['travel_class'].lower():
                                filtered_flights.append(flight)

                return render(request, 'core/flight_results.html', {"from": model.From.departure_city.capitalize(),
                                                                    "to": model.to.arrival_city.capitalize(),
                                                                    "filtered_flights": filtered_flights})

            elif model.transport_type.transport == 'train':
                url = create_train_url(model)
                filtered_trains = []
                if url != "":
                    trains_response = requests.get(url).json()
                    if 'results' in trains_response:
                        for train in trains_response['results']:
                            if model.ticket_class.Class in train['itineraries']['trains']['prices']['service_class'].lower():
                                if model.price is not None:
                                    if model.price.price <= train['itineraries']['trains']['prices']['total_price'].amount and model.price.currency == train['itineraries']['trains']['prices']['total_price'].currency.lower():
                                        filtered_trains.append(train)
                                else:
                                    filtered_trains.append(train)

                return render(request, 'core/train_results.html', {"from": model.From.departure_city.capitalize(),
                                                                   "to": model.to.arrival_city.capitalize(),
                                                                   "filtered_trains": filtered_trains})
            elif model.transport_type.transport == 'bus':
                return render(request, 'core/bus_results.html')

        except TextXSyntaxError as error:
            return render(request, self.template_name, {'form': form, 'error_message': syntax_error_message(str(error))})
        except TextXSemanticError as error:
            return render(request, self.template_name, {'form': form, 'error_message': error})


def syntax_error_message(error):
    if error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|one-way|round-trip))'"):
        return "You didn't define number of tickets or ticket type (one-way or round-trip)."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|economy|business|first|second|couchette))'"):
        return "You must define ticket class."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|plane|bus|train))'"):
        return "You must define mean of transport (plane, train or bus)."
    elif error.startswith("Expected '.*?(?=(^\s*|\s+)(\/\*|'|[1-9]\d*))'"):
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


def create_flight_url(model):
    departure_city_code = ""
    arrival_city_code = ""

    if City.objects.filter(name=model.From.departure_city).exists():
        departure_city_code = City.objects.get(name=model.From.departure_city).iata_code
    if City.objects.filter(name=model.to.arrival_city).exists():
        arrival_city_code = City.objects.get(name=model.to.arrival_city).iata_code

    flights_url = ""

    if model.ticket_type.type == 'round-trip':
        if model.price is not None:
            total_price = int(model.number_of_tickets.number) * int(model.price.price)
            flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                          '&destination=' + arrival_city_code + \
                          '&departure_date=' + model.on.departure_date + \
                          '&return_date=' + model.return_date.return_date + \
                          '&adults=' + model.number_of_tickets.number + \
                          '&max_price=' + str(total_price) + \
                          '&currency=' + model.currency.currency
        else:
            flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                          '&destination=' + arrival_city_code + \
                          '&departure_date=' + model.on.departure_date + \
                          '&return_date=' + model.return_date.return_date + \
                          '&adults=' + model.number_of_tickets.number
    else:
        if model.price is not None:
            total_price = int(model.number_of_tickets.number) * int(model.price.price)
            flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                          '&destination=' + arrival_city_code + \
                          '&departure_date=' + model.on.departure_date + \
                          '&adults=' + model.number_of_tickets.number + \
                          '&max_price=' + str(total_price) + \
                          '&currency=' + model.currency.currency
        else:
            flights_url = 'https://api.sandbox.amadeus.com/v1.2/flights/affiliate-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                          '&destination=' + arrival_city_code + \
                          '&departure_date=' + model.on.departure_date + \
                          '&adults=' + model.number_of_tickets.number
    return flights_url


def create_train_url(model):
    departure_city = model.From.departure_city
    arrival_city = model.to.arrival_city

    departure_city_url = 'https://api.sandbox.amadeus.com/v1.2/rail-stations/autocomplete?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&term=' + departure_city
    arrival_city_url = 'https://api.sandbox.amadeus.com/v1.2/rail-stations/autocomplete?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&term=' + arrival_city
    departure_city_response = requests.get(departure_city_url).json()
    arrival_city_response = requests.get(arrival_city_url).json()

    if departure_city_response and arrival_city_response:
        departure_city_code = departure_city_response[0]['value']
        arrival_city_code = arrival_city_response[0]['value']

        trains_url = 'https://api.sandbox.amadeus.com/v1.2/trains/extensive-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + departure_city_code + \
                     '&destination=' + arrival_city_code + \
                     '&departure_date=' + model.on.departure_date

        if model.ticket_type.type == 'round-trip':
            return_trains_url = 'https://api.sandbox.amadeus.com/v1.2/trains/extensive-search?apikey=rWjxYGjkHiSxAwDXK0LF1a5LNmtAYZ2z&origin=' + arrival_city_code + \
                                '&destination=' + departure_city_code + \
                                '&departure_date=' + model.return_date.return_date
            return_trains_response = requests.get(return_trains_url).json()
            if 'results' not in return_trains_response:
                return ""

        print(departure_city_code)
        print(arrival_city_code)
        return trains_url
    return ""

