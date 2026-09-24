# Notes for Claude

- Amazon links: Katie is an Amazon Associate (tag in `_config.yml` →
  `amazon.tag`). Always link Amazon products through
  `_includes/amazon-url.html` (or `book-card.html` for her books in
  `_data/books.yml`), never a bare untagged URL, and never remove the
  disclosure. The build plugin `_plugins/amazon_affiliate.rb` adds the tag,
  `rel="sponsored"`, and the disclosure note automatically; see README
  "Books and Amazon affiliate links".
- Styles come from the Katie Allred design system; use the tokens at the top
  of `assets/css/main.css`.
