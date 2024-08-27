# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class CustomButton(Component):
    """A CustomButton component.
CustomButton is an example component that shows a bouncing button.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- className (string; optional):
    The className of the button. This is used to apply custom styles
    to the button.

- color (string; optional):
    The color of the button. This should be a Bootstrap color name.

- label (string; required):
    A label that will be printed when this component is rendered."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'demo'
    _type = 'CustomButton'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, label=Component.REQUIRED, color=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'className', 'color', 'label']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'className', 'color', 'label']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['label']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(CustomButton, self).__init__(**args)
