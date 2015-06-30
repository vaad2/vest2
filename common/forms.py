from django import forms

# USAGE:
# class _Form(ExModelForm):
# rx_attrs = {'username': {'placeholder': 'user name', 'class' : 'class name'}}

# adds placeholder from from model or rx_atrrs

class ExModelForm(forms.ModelForm):
    rx_attrs = {}

    def __init__(self, *args, **kwargs):
        super(ExModelForm, self).__init__(*args, **kwargs)

        # for field in self.instance._meta
        for form_key, form_field in self.fields.iteritems():
            if '_all' in self.rx_attrs:
                form_field.widget.attrs.update(self.rx_attrs['_all'])

            if hasattr(self.instance, form_key):
                self.fields[form_key].widget.attrs['placeholder'] = \
                    self.instance._meta.get_field_by_name(form_key)[0].verbose_name.title()
            elif self.fields[form_key].label:
                self.fields[form_key].widget.attrs['placeholder'] = \
                    self.fields[form_key].label



        for key, val in self.rx_attrs.iteritems():
            if key in self.fields:
                self.fields[key].widget.attrs.update(val)



class ExForm(forms.Form):
    rx_attrs = {}

    def __init__(self, *args, **kwargs):
        super(ExForm, self).__init__(*args, **kwargs)

        for form_key, form_field in self.fields.iteritems():
            if '_all' in self.rx_attrs:
                form_field.widget.attrs.update(self.rx_attrs['_all'])

            self.fields[form_key].widget.attrs['placeholder'] = \
                self.fields[form_key].label

        for key, val in self.rx_attrs.iteritems():
            if key in self.fields:
                self.fields[key].widget.attrs.update(val)

