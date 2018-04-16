{{ fullname | escape | underline }}

.. rubric:: Description

.. automodule:: {{ fullname }}
.. currentmodule:: {{ fullname }}


{% if classes %}
.. rubric:: Classes

.. autosummary::
    :toctree: generated/
    {% for class in classes %}
    {{ class }}
    {% endfor %}

{% endif %}

{% if functions %}
.. rubric:: Functions

.. autosummary::
    :toctree: generated/
    {% for function in functions %}
    {{ function }}
    {% endfor %}

{% endif %}