from django import forms

class OrderFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "placeholder": "Пошук за назвою",
                "class": "px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        })
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "placeholder": "Початкова дата",
                "class": "px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "placeholder": "Кінцева дата",
                "class": "px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    min_volume = forms.FloatField(
        required=False,
        label="Мінімальний обʼєм",
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "placeholder": "Мінімальний обʼєм",
                "class": "px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    max_volume = forms.FloatField(
        required=False,
        label="Максимальний обʼєм",
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "placeholder": "Мінімальний обʼєм",
                "class": "px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    min_price = forms.FloatField(
        required=False,
        label="Мінімальна ціна (USD)",
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "placeholder": "Мінімальна ціна",
                "class": "px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
    max_price = forms.FloatField(
        required=False,
        label="Максимальна ціна (USD)",
        widget=forms.NumberInput(
            attrs={
                "type": "number",
                "placeholder": "Максимальна ціна",
                "class": "px-3 py-2 rounded bg-gray-800 text-white border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            }
        )
    )
