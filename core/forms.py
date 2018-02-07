from django import forms


class QueryForm(forms.Form):
    query = forms.CharField(label='Please describe desired ticket', required=True,
                            widget=forms.Textarea(attrs={'rows': 15, 'cols': 75, 'style': 'resize:none;'}))


