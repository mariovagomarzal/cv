// Strong text in small caps, as quire does, since it sets EB Garamond without bold.
#show strong: it => smallcaps(it.body)

// The dates and locations are quiet labels, as quire sets them: light, muted Fira Sans.
#show grid.cell.where(x: 1): set text(font: "Fira Sans", weight: "light", size: 0.8em, fill: luma(50%))

// Links keep the text color and are underlined with a thin muted rule.
#show underline: set underline(stroke: 0.3pt + luma(50%), offset: 2.5pt)

// The bullets are en dashes, as in quire's lists.
#show list: set list(marker: [–])

// The external link icon is the arrow that marks links on my website, in muted Fira Sans like the dates.
#import "@preview/fontawesome:0.6.0": fa-icon-map-common
#show fa-icon-map-common.at("external-link"): text(font: "Fira Sans", size: 1.3em, baseline: 0.25em, fill: luma(50%))[↗]
