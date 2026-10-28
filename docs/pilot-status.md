# WordPress conversion pilot

Generated 2026-10-28 using the configuration in
`migration/config.example.toml`. The original WordPress sources were not modified.

## Result

- All 316 WXR records normalized; 175 published post/page routes identified.
- All nine selected pilot articles staged in `migration/work/pilot-candidate/`.
- 12 local code blocks retained; three GitHub gist scripts retained as remote
  embeds by owner request. No gist files downloaded or included locally.
- 26 referenced public media files copied with source/output SHA-256 checks.
- Comments omitted; three drafts and non-article custom records excluded from
  the public pilot. Normalized nonpublic HTML remains only in ignored work data.
- Tabs converted to headings; slider 775 converted to an ordered static gallery
  with captions and links to attachment originals.
- Existing encrypted PayPal contribution form retained for browser review.

The pilot is a candidate for review, not an accepted release. Its templates and
placeholder domain remain the scaffold defaults. Full-site links may target
articles outside the selected nine and therefore absent from this partial site.

## Verification

`python3 -m unittest discover -s tests -v`: 21 synthetic regression tests passed.
These cover XML entity rejection, duplicate IDs/routes, traversal and symlink
escapes, private-content exclusion, comment omission, code whitespace/entities,
multiple/nested code blocks, long fences, media checks, remote gist policy,
determinism, and protection of editorial changes.

Markdown prose now preserves literal quotes, apostrophes, and Unicode, with
Markdown escaping only where syntax needs protection. Article directories use
descriptive source slugs instead of `wp-ID`, with IDs retained in metadata.
The previous pilot is preserved in `migration/work/pilot-before-markdown-cleanup/`.
Comparing its built output with the updated pilot confirmed identical article
text, public paths, and rendered code payloads.

Repeated real-source conversion produced identical staging files and report
fingerprints. `validate` reports zero blocking findings for the implemented
source/output integrity checks. Detailed ignored reports are in
`migration/reports/pipeline/`; command usage is in `scripts/README.md`.

Zola 0.23.6 is installed and pinned in `.zola-version`. The official Linux GNU
archive was verified against the release API's SHA-256 digest:
`8f5132b3522412d04e395e0b25f6d68613ad272a873e54a2b3ebf664873024a4`.
Both the scaffold and nine-page pilot pass `zola build` and
`zola check --skip-external-links`. External URLs were not requested by these
checks. No browser review was completed. Rendered code fidelity, desktop/mobile appearance, gist
loading, media playback, PayPal behavior, and full link/fragment coverage remain
unverified. Static search will not index code dynamically inserted by GitHub.

## Next acceptance step

Preview the staged site with `zola --root migration/work/pilot-candidate serve`
and compare each pilot page against its mirrored WordPress counterpart. Resolve review findings
through the converter or explicit configuration, regenerating into a fresh
staging directory. Only then expand conversion to the full corpus and finish
routes, design, feeds, and search.
