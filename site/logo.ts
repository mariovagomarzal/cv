// Prints the logo as JSON: the favicon, and the inline mark, which takes the color of the text around it.
import { logoPresets, logoSvg } from "npm:@mariovagomarzal/lattice@0.2.0/logo";

console.log(
  JSON.stringify({
    favicon: logoSvg(logoPresets.favicon),
    inline: logoSvg({ ...logoPresets.inline, ink: "currentColor" }),
  }),
);
