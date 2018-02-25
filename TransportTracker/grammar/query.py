import datetime

from textx.exceptions import TextXSemanticError


class TicketQuery(object):

    def interpret(self, model):
        model.From.departure_city = city_name_processor(model.From.departure_city)
        model.From.arrival_city = city_name_processor(model.to.arrival_city)
        ticket_class_processor(model.transport_type.transport, model.ticket_class)
        cities_processor(model.From.departure_city, model.to.arrival_city)
        model.on.departure_date = date_format_processor(model.on.departure_date)
        round_trip_processor(model.ticket_type.type, model.return_date)
        if model.return_date is not None:
            model.return_date.return_date = date_format_processor(model.return_date.return_date)
            date_processor(model.on.departure_date, model.return_date.return_date)
        price_currency_processor(model.price, model.currency)


def city_name_processor(city):
    return city.replace('-', ' ')


def ticket_class_processor(transport_type, ticket_class):
    if transport_type != 'bus':
        if ticket_class is None:
            raise TextXSemanticError('Ticket class must be defined.')
        else:
            if transport_type == 'plane' and ticket_class.Class != 'economy' and ticket_class.Class != 'business':
                raise TextXSemanticError('Plane ticket class must be economy or business.')
            elif transport_type == 'train' and ticket_class.Class != 'first' and ticket_class.Class != 'second' and ticket_class.Class != 'couchette':
                raise TextXSemanticError('Train ticket class must be first, second or couchette.')


def cities_processor(departure_city, arrival_city):
    if departure_city == arrival_city:
        raise TextXSemanticError('Departure and arrival city cannot be the same.')


def round_trip_processor(ticket_type, return_date):
    if ticket_type == 'round-trip' and return_date is None:
        raise TextXSemanticError('You must specify return date for round-trip ticket.')


def date_format_processor(date):
    date = date.replace('.', '/')

    day = date.split('/')[0]
    month = date.split('/')[1]
    year = date.split('/')[2]

    try:
        datetime.date(year=int(year), month=int(month), day=int(day))
        return datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
    except:
        raise TextXSemanticError('Departure or return date is not valid.')


def date_processor(departure_date, return_date):
    if return_date < departure_date:
        raise TextXSemanticError('Return date must be after departure.')


def price_currency_processor(price, currency):
    if price is not None and currency is None:
        raise TextXSemanticError('You must specify currency for the maximum price.')
    elif currency is not None and price is None:
        raise TextXSemanticError('You must specify maximum price for the ticket.')

