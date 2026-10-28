# Live WordPress versus full staging audit

Audit performed 2026-10-28 against `https://zderadicka.eu` and the staging build
at commit `e076963`. This report proposes changes; it does not implement them.

## Scope and coverage

The public WordPress REST API returned 154 posts and 21 pages. All 175 IDs,
canonical article paths, and local publication timestamps match the migration
records. Every corresponding live HTML page was retrieved successfully; transient
connection timeouts were retried. There are no live-only or export-only published
post/page IDs in this comparison.

All 175 article bodies were compared with staging:

| Check | Result |
| --- | --- |
| Block-code text | 434 samples, exact match |
| Inline-code text | 830 samples, exact match |
| Inline/gallery image references | 112 image occurrences; paths, order, multiplicities, and alt text match |
| Native audio/video source paths | Match on every page |
| Gist script references | All eight preserved |
| HTML table counts | Match on every page |
| Normalized prose | 162 pages match exactly after case, whitespace, and punctuation normalization; all 13 other differences reviewed |

The prose differences are explained by tab labels moving into headings, gallery
captions becoming visible text, omission of plugin attribution/player fallback
URLs, WordPress typography such as `28×28` versus source `28x28`, and the one
missing automatic YouTube embed described below. No unexplained article prose
loss was found. This is a content comparison, not pixel identity.

Eight representative routes were rendered directly from both sites at 1440px
and 390px viewport widths: homepage, Tiny Etude in Generics, MyBookshelf, Visual
Python video, audio captchas, imap_detach tables, Rust generics gist, and the latest
MyBookShelf 4 post. These produced 32 screenshots. Lower-page tables, galleries,
and the YouTube discrepancy were also inspected in 12 detail captures; those
live-side detail views used cached live HTML with its original styles/assets to
avoid repeated slow WordPress document requests.

## Prioritized findings

### 1. Restore highlighting in retained HTML code blocks

**Priority: high.** The nine samples in Tiny Etude in Generics are now highlighted,
confirming the preceding fix. However, 56 other block samples across 20 pages are
emitted as raw `pre/code` HTML and bypass Zola highlighting. Of these, 54 carry
explicit language labels on the live site; two have no explicit live language.
Their code text is intact.

Examples:

- [MyBookshelf](https://zderadicka.eu/projects/python/mybookshelf-ebooks-library/):
  three blocks retained inside HTML, including the Apache configuration.
- [rest2backbone](https://zderadicka.eu/projects/python/rest2backbone/): six blocks.
- [Oracle LOB compression](https://zderadicka.eu/oracle-db-compression-of-lobs/):
  six PL/SQL samples.

The remaining fallback handles nested HTML containers and template delimiters.
Preserve language-aware highlighting in these cases without compromising the
existing exact-text checks. Extend the rendered audit to verify highlighting
eligibility, not only payload equality.

### 2. Convert WordPress automatic embeds

**Priority: high.** On
[Audioserve Android Client Early Beta](https://zderadicka.eu/audioserve-android-client-early-beta-is-available/),
WordPress turns a bare YouTube URL into a player for video `EGfTJuSiGeE`. Staging
shows the URL as plain text. This is the only iframe-source discrepancy found
across all 175 bodies; explicit embed shortcodes are preserved.

Recognize supported standalone provider URLs, retain their player, and provide a
normal link as fallback. Do not modify URLs inside code or ordinary prose.

### 3. Recreate the site structure and navigation

**Priority: high for completion, rather than a content-conversion defect.** The
live site has a logo/tagline, black header and sidebar, project hierarchy,
About/Contact/Contribute navigation, tag/category/month archives, search, and
previous/next article links. Staging has a single Ivanovo header link.

The live homepage has excerpts and pagination (16 index pages); staging presents
one long list of all articles and project pages. Separate posts from project
pages, restore useful navigation and excerpts, and implement archive/feed/search
compatibility. Existing `/feed/`, `/page/N/`, category/tag/month/author archive
routes are not yet covered by the article-path completeness result.

### 4. Restore table styling

**Priority: medium; directly affects technical readability.** The
[imap_detach reference](https://zderadicka.eu/projects/python/imap_detach-tool-download-email-attachments/)
has clear bordered cells and padding on the live site. Staging retains table
structure and text but displays tightly packed borderless cells. Add consistent
borders, padding, alignment, and a narrow-screen scroll container where needed.

### 5. Bring typography and code presentation closer

**Priority: medium.** On the measured desktop article example, live body text is
Lato 16px with 24px line height; staging uses system-ui 17.6px with 29.04px line
height. Staging headings are heavier, links blue rather than green, and the
background/sidebar treatment is absent. These differences are conspicuous on
mobile, where introductory text takes substantially more vertical space.

Code contents and the fixed generics highlighting are correct, but line numbers,
striped rows, the left rule, colors, and spacing differ from the live Enlighter
presentation. Match the broad visual treatment while preserving horizontal
scrolling and exact code content.

Project pages also gain a publication date in staging where the live project
layout does not show one. Post author/category/tag metadata is retained in data
but not rendered as on the live site. Use distinct post/project templates.

### 6. Confirm tabs and gallery presentation

**Priority: preference/visual decision.** Four tabbed project pages are expanded
into sequential sections; five image sliders become static galleries. Images,
order, captions, and full-size links are preserved. This deliberately changes
interaction and page length. Keep the simpler static approach if preferred, or
restore accessible tabs/carousels during theme work.

### 7. Restore responsive image delivery

**Priority: medium for mobile performance.** Although image contents/references
are present, 68 image occurrences on 41 pages lack the `srcset` supplied by live
WordPress. Another 23 occurrences on nine pages lack its lazy-loading attribute.
These do not remove images, but can increase mobile downloads and initial-page
work. Recreate responsive candidates using preserved image variants and add
appropriate lazy loading, while keeping original/full-size links intact.

## What worked in the browser samples

- The Tiny Etude page shows all nine examples with syntax colors.
- The sampled GitHub gist renders remotely on both live and staging pages.
- Native video and three audio samples reach loaded/buffered states in staging.
- No page-wide horizontal overflow appeared in the eight representative routes
  at either viewport size; this is not a claim about every article/device.
- Images in the sampled staging pages loaded. Some hidden/lazy live gallery and
  offscreen images were not loaded at capture time; these were not classified as
  migration losses or proven live-site failures.

Comments remain intentionally omitted under the owner's policy. They are not a
coverage defect. Gallery expansion, typography normalization, and native player
fallback text differences were also distinguished from lost article text.

## Evidence and limits

Detailed local artifacts are ignored under `migration/reports/live-audit/`:
`live-inventory.json`, `content-comparison.json`, `summary.json`, cached HTTP
responses, `browser/metrics.json` with 32 screenshots, and `details/` with 12
additional screenshots. They are review evidence, not publishing inputs.

The audit compared all article bodies and media references, but did not hash all
live media binaries, watch every video, exercise every carousel, or submit the
PayPal/contact forms. Code text was compared in server HTML; representative
client-side rendering was checked in Chromium. Not all 175 pages were visually
reviewed at both widths. Source wording/punctuation normalization is not proof
of identical emphasis, layout, accessibility, or third-party service availability.
No site implementation or migration source files were changed by this audit.
