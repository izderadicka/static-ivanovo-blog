# Full content staging

Converted on 2026-10-28 using `migration/full.example.toml` and Zola 0.23.6.
The site is in ignored `migration/work/full-site/`; original WordPress inputs
and curated `content/` are unchanged. The original pilot is also preserved.

```sh
zola --root migration/work/full-site serve
```

## Coverage

- All 154 published posts and 21 published pages map to their original public
  paths, in descriptive content directories with WordPress IDs in metadata.
- Three drafts are excluded. Comments are omitted, including comment contact data.
- All 434 block-code payloads and 830 inline-code payloads match the rendered HTML.
  Prose checks confirm source words remain in order; added gallery captions and
  tab headings are allowed. These automated checks do not replace visual review.
- 176 original/referenced media files total 63,209,779 bytes. Both staging and built
  copies match source SHA-256 checksums. Statistics files, backups, and PHP files
  are not copied to the public output.
- 128 attachment paths plus one historical attachment URL are preserved through
  HTML redirects to original files. Internal attachment links go directly to media.
- 675 local URL references resolve, including checks of HTML fragment targets.
- Five sliders become static galleries preserving image order/captions and links
  to originals. Uploaded audio/video and YouTube embeds retain their content.
- Eight gist embeds remain remote GitHub scripts, per owner policy. No gist
  downloads were made. The original PayPal contribution form remains for review.
- The source origin/title are set to `https://zderadicka.eu` / Ivanovo in staging.

## Resolved full-corpus cases

Legacy highlighting labels are recognized. Samples containing Django template
syntax use escaped HTML so Zola cannot execute their delimiters. Inline code uses
Markdown spans or escaped HTML, preserving underscores, tildes, and multiline
payloads. Code in retained HTML lists uses newline character references because
blank lines otherwise end Markdown HTML blocks. Highlighted fences account for
Giallo's removal of the final newline; built text comparisons enforce exact output.

WordPress read-more markers become `more-ID` anchors. This preserves list text
which Zola otherwise discards when its summary marker occurs on the same line.
The historical `/thethe-slider/thetool/` mapping was verified using the mirror's
attachment image, then recorded explicitly in the full configuration.

## Verification and reports

The 25 regression tests pass, including a real Zola build of synthetic samples,
negative checks for altered rendered code, broken fragments, and changed media,
and checks for private attachment parents and query-route rewriting.

Code highlighting also covers fenced samples without a final newline. An earlier
HTML fallback preserved their text but skipped highlighting; it was removed after
a regression test reproduced the problem. All nine samples in
`/tiny-etude-in-generics/` now have syntax colors, with exact code payloads intact.

Full conversion reruns deterministically. `zola build`,
`zola check --skip-external-links`, and migration validation pass with zero blocking
findings in the implemented checks. Detailed ignored reports are under
`migration/reports/full/`: `inventory.json`, `exclusions.json`, `conversion.json`,
`validation.json`, and `rendered-validation.json`. Normalized source records remain
in ignored `migration/work/normalized/`.

There are 14 explicit review items: five gallery conversions, the contribution
form, and eight gist scripts. External references (749 distinct URLs) are listed
without requesting them; no claim is made about third-party availability.

## Remaining acceptance work

The subsequent [live-site comparison](live-site-audit.md) confirms coverage of
all 175 published bodies and exact block/inline code text, while identifying
remaining highlighting, automatic-embed, responsive-image, and visual parity gaps.

This is full content staging, not a production release. Representative
desktop/mobile views and gist/media loading have now been reviewed in the live
audit. Exhaustive visual review, full media playback, and PayPal behavior remain
unverified.
Typography/layout remain the scaffold defaults. Required taxonomies are retained
in metadata, but their archive pages and navigation still need implementation.

Next: review representative full-corpus pages, then complete theme/navigation,
archives, canonical metadata, feed compatibility, search, and the 404 page. Historic
archive/feed URLs, pagination, and arbitrary inbound `?p=ID` routing still need
mapping and host configuration. HTML attachment redirects are not HTTP 301/308
responses. Fragment checks cover links found in migrated article HTML; arbitrary
inbound fragment identifiers have not all been inventoried. Server-specific redirects and final browser
acceptance precede promotion/cutover; no deployment was attempted.
