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
{#
  Sections of bullets, such as the research interests, are set in two columns: their list is laid out as a table
  (not a grid, whose second column the design styles as dates), closed by `SectionEnding.j2.typ`.
#}
{% if entry_type == "BulletEntry" %}
#[
#show list: it => table(
  columns: (auto, auto),
  stroke: none,
  inset: 0pt,
  column-gutter: 3em,
  row-gutter: 0.9em,
  ..it.children.map(item => par(justify: false, hanging-indent: 1em, box(width: 1em)[–] + item.body)),
)
{% endif %}
