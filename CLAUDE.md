# Notes for Claude

@MAINTAINING.md holds the full maintainer notes (structure, design, SEO,
deploying, content conventions). The repo is public: never commit secrets.

- Amazon links: Katie is an Amazon Associate (tag in `_config.yml` →
  `amazon.tag`). Always link Amazon products through
  `_includes/amazon-url.html` (or `book-card.html` for her books in
  `_data/books.yml`), never a bare untagged URL, and never remove the
  disclosure. The build plugin `_plugins/amazon_affiliate.rb` adds the tag,
  `rel="sponsored"`, and the disclosure note automatically; see MAINTAINING.md
  "Books and Amazon affiliate links".
- Styles come from the Katie Allred design system; use the tokens at the top
  of `assets/css/main.css`.
- SEO/AEO: `_includes/seo.html` builds all head metadata and JSON-LD from
  front matter and `_data/schema.yml`. Give every new page or post a
  `description`; put FAQs in `faq:` front matter and render them with
  `faq.html` so the FAQPage data matches the page. See MAINTAINING.md "SEO and
  answer engines".
- Share images: pages and posts without `image` get a generated Open Graph
  card (`_plugins/og_images.rb` + `scripts/og_image.py`, needs Pillow). Set
  `og_title` when the page title reads badly on the card.
- IndexNow: each deploy submits new, removed and updated URLs (by sitemap
  `last_modified_at`) via `scripts/indexnow.py`. Bump `last_modified_at` when
  editing a page or post. See MAINTAINING.md "SEO and answer engines".
