import datetime
from django import template

register = template.Library()


@register.filter
def time_filter(train_date_time):
    date = datetime.datetime.strptime(train_date_time.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
    time = train_date_time.split('T')[1]
    return "on " + date + " at " + time