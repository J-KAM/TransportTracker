from django.shortcuts import render
from django.views import View

from core.forms import QueryForm

from textx.exceptions import TextXSyntaxError
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
        except TextXSyntaxError:
            return render(request, self.template_name, {'form': form, 'error_message': 'Syntax error'})

        return render(request, self.template_name, {'form': form, 'error_message': ''})
