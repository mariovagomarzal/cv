// The external link icon is the arrow that marks links on my website, instead of the Font Awesome one. If its glyph
// ever changes, RenderCV's icon simply shows again.
#import "@preview/fontawesome:0.6.0": fa-icon-map-common
#show fa-icon-map-common.at("external-link"): text(font: "Space Grotesk", size: 1.5em)[↗]

// The bullets are a glyph of lattice's ramp. A show-set rule, since RenderCV sets its own marker in every entry.
#show list: set list(marker: text(font: "Space Mono", size: 0.85em)[\*])
