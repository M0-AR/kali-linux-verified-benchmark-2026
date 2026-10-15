# Contributing

1. Pick one claim in `data/book_claims.csv`.
2. Verify it against a live public source (docs page or API) + a sandbox run where possible.
3. Update the CSV + the experiment that checks it — never edit numbers by hand.
4. Run `docker compose up --build` and confirm `results/*.json` regenerate cleanly.
5. Open a PR with the source link + before/after JSON diff.
