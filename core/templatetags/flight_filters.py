import datetime
from django import template

register = template.Library()

@register.filter
def flight_type(flights):
    if len(flights) > 1:
        return "transfer"
    else:
        return "direct"

@register.filter
def departure(flights):
    date_time = flights[0]['departs_at']
    date = datetime.datetime.strptime(date_time.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    time = date_time.split('T')[1]
    return "on " + date + " at " + time

@register.filter
def arrival(flights):
    date_time = flights[-1]['arrives_at']
    date = datetime.datetime.strptime(date_time.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    time = date_time.split('T')[1]
    return "on " + date + " at " + time