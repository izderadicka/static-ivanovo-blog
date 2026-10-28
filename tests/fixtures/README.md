# Migration fixtures

Add small synthetic or sanitized WXR/HTML examples when implementing the importer.
Cover code whitespace/entities/backticks, plugin shortcodes, non-ASCII URLs,
media variants, embeds, private posts, malformed input, and route collisions.
Do not commit real private exports. Expected results must assert content fidelity,
not merely mirror implementation details.
