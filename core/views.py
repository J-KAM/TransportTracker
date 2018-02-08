from django.shortcuts import render
from django.views import View

from TransportTracker.grammar.query import TicketQuery
from core.forms import QueryForm

from textx.exceptions import TextXSyntaxError, TextXSemanticError
import os
from TransportTracker.settings import BASE_DIR
from TransportTracker.execute.execute import execute_for_web


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

        except TextXSyntaxError as error:
            return render(request, self.template_name, {'form': form, 'error_message': syntax_error_message(str(error))})
        except TextXSemanticError as error:
            return render(request, self.template_name, {'form': form, 'error_message': error})

        return render(request, self.template_name, {'form': form, 'error_message': ''})


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

