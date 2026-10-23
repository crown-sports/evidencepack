# Recreate the API-results figure

The README figure is a documentation layout of real `pack()` / `verify()` output.
It is not an application screen and it does not contain model output.

From a main checkout, after installing the package:

```sh
python docs/render_example.py
```

This writes `docs/assets/readme-demo.json` and `docs/assets/readme-demo.html`.
Open the HTML in a browser at **1200 × 850**, then capture the viewport as
`docs/assets/pack-verify.png`. The committed image was captured with Chromium.
The renderer uses the same generated inputs and query as `examples.quickstart`;
receipt/artifact identifiers change on each run, while the excerpt contents,
1,177-byte pack and two verdicts remain the same.

The 2,000-byte budget includes metadata. Only the configuration excerpt is
expanded in the figure; the saved JSON contains all five excerpts. The layout
wraps its one source line visually without changing the stored quote.
