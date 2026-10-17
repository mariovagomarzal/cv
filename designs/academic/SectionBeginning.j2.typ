{# The section titles take the color of their rule, so the title is wrapped to keep it in the text color. #}
{% set section_title = '#text(fill: rgb("#000000"))[' ~ section_title ~ ']' %}
{% include "typst/SectionBeginning.j2.typ" %}
