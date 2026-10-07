# Notes for Claude

@MAINTAINING.md holds the full maintainer notes (structure, design, SEO,
deploying, content conventions). The repo is public: never commit secrets.

- Screenshots: never commit screenshots you take while working (before/after
  views, previews, browser-automation captures). Keep them in a scratch
  directory and share them in chat. Only images meant for the public site go
  in `assets/`, and never ones showing logged-in dashboards, inboxes,
  analytics, billing, client data or credentials.

- Amazon links: Katie is an Amazon Associate (tag in `_config.yml` →
  `amazon.tag`). Always link Amazon products through
  `_includes/amazon-url.html` (or `book-card.html` for her books in
  `_data/books.yml`), never a bare untagged URL, and never remove the
  disclosure. The build plugin `_plugins/amazon_affiliate.rb` adds the tag,
  `rel="sponsored"`, and the disclosure note automatically; see MAINTAINING.md
  "Books and Amazon affiliate links".
- Amazon product pictures: Associates rules only allow images from the
  Product Advertising API, loaded from Amazon's own URLs. Never download,
  screenshot or commit an Amazon product image. For a post that lists
  products, set `product_images: true` in its front matter: the Pages
  workflow runs `scripts/amazon_products.py` (keys from repository secrets)
  to write `_data/amazon_products.json` (gitignored), and
  `_plugins/amazon_product_images.rb` puts a linked thumbnail in front of
  each table cell or list item that starts with an Amazon product link. See
  MAINTAINING.md "Amazon product thumbnails".
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
- Social media (Zernio): never share, schedule or publish a social post that
  links a blog post until `python3 scripts/check_live.py <post file or URL>`
  says LIVE. Schedule shares for after the post is live (a post dated 08:00
  Central is live by about 09:15). See MAINTAINING.md "Sharing posts on
  social media".
