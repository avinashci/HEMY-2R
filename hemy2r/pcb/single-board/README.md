# Single board (experiment)

polvinc's **TeenAstro HEMY Redux v2.6.5M** main board and **HEMY Brake Driver 1.1** merged into one board for the HEMY 2R cube, with the [design review](../../docs/design-review.md)'s electrical fixes built in.

> **Not ready to order.** This is an experiment that needs a review by someone with PCB experience. Build #1 uses polvinc's two boards ([`../jlc-order/`](../jlc-order/)).

## Files

| File | What |
|---|---|
| `HEMY-2R-board.epro` | EasyEDA Pro project (schematic + PCB). Open in EasyEDA Pro 2.2+. |
| `HEMY-2R-board-schematic.pdf` | All schematic pages |
| `HEMY-2R-board-BOM.csv` | Bill of materials with LCSC part numbers |
| `HEMY-2R-board-netlist.json` | Netlist (EasyEDA JSON format) |
| `brake_page.json`, `brake_connect.json`, `place_batch.js` | Scripts used to build the Brake page through EasyEDA Copilot |

## Progress

See [electronics](../../docs/04-electronics.md#single-board-experiment) for the step list and the parts on the Brake page.

## Notes

- Schematic pages: **Logic**, **Power** (polvinc's), **Brake** (new).
- Nets cross pages by name: `VCC` (protected 12 V), `+3.3V`, `GND`, `M1_ENA`. Brake-only nets start with `BRK_`.
- The PCB layout is still polvinc's with an enlarged outline (82.5 × 57 mm + a corner tab); the new parts haven't been placed yet.
- polvinc's title-block frame on the Logic page was removed: it was a malformed part that stopped EasyEDA exporting the netlist.
