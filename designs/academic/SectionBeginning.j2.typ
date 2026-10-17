{#
  The rule runs under the title and leaves a gap around the letters that cross it, as an underline does: the title is
  underlined and a line at the same height takes the rule to the margin. Its thickness and color come from the design.
#}
{% set section_title = '#context {'
  ~ ' let config = rendercv-config.get();'
  ~ ' let rule = config.at("section-titles-line-thickness") + config.at("colors-section-titles");'
  ~ ' underline(stroke: rule, offset: 0.12em, evade: true, text(fill: config.at("colors-body"))[' ~ section_title ~ ']);'
  ~ ' box(width: 1fr, height: 0pt, place(dy: 0.12em, line(length: 100%, stroke: rule)))'
  ~ ' }' %}
{% include "typst/SectionBeginning.j2.typ" %}
