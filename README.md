# personal

Personal website and blog, built with [Jekyll](https://jekyllrb.com).

## Local development

```sh
bundle install
bundle exec jekyll serve          # http://127.0.0.1:4000
bundle exec jekyll serve --drafts # include _drafts/ in the preview
bundle exec jekyll build          # output to _site/
```

## Structure

```
_config.yml        Site metadata, contact details, permalinks, plugins
_data/             navigation, social links (fixed order), hero links
_layouts/          default, page, post, home, landing, legal, blank
_includes/         header, footer, post-card, pagination
.github/workflows/ pages.yml builds and deploys to GitHub Pages
_posts/            Published posts (YYYY-MM-DD-slug.md)
_drafts/           Undated drafts, only built with --drafts
assets/css|js|images
pages/             Site pages imported from WordPress (home, about, services…)
blog/index.html    Blog (paginated post list, /blog/)
archive.html       Posts grouped by year
tags.html          Posts grouped by tag
```

## Design

Styles in `assets/css/main.css` come from the **Katie Allred** design system
(https://claude.ai/artifact/DJYQV3tu5rDPEBrhrLuuw6): its color, type, spacing,
radius and shadow tokens, plus the Button, Chip, Wordmark, WaveBand,
ContentCard and Footer components. Fonts (Bricolage Grotesque, DM Sans,
Caveat) are self-hosted in `assets/fonts/` and declared in
`assets/css/fonts.css`, so pages never call Google's servers. When the design
system changes, update the tokens at the top of `main.css` to match; to add a
font or weight, download its woff2 files into `assets/fonts/` and add matching
`@font-face` rules to `fonts.css`.

## Books and Amazon affiliate links

Katie is an Amazon Associate (tag `kajal04-20`, set as `amazon.tag` in
`_config.yml`). Her books live in `_data/books.yml` with covers in
`assets/images/books/`; show one with `{% include book-card.html book=book %}`.
For any other Amazon product, link with
`{% include amazon-url.html asin="ASIN" %}` or just paste the Amazon URL.

`_plugins/amazon_affiliate.rb` handles the rest at build time:

- Every `amazon.com` link gets the affiliate tag (product links become clean
  `/dp/ASIN/?tag=…` URLs); every Amazon or `amzn.to` link gets
  `rel="sponsored nofollow noopener"`.
- Any page or post that mentions Amazon is flagged `affiliate_links: true`,
  and the layouts show `_includes/affiliate-note.html` ("As an Amazon
  Associate I earn from qualifying purchases"): at the top of posts, above
  the footer on other pages. To place it yourself, include it and set
  `affiliate_note: inline`; to opt a page out, set `affiliate_links: false`.

## Deploying

Pushes to `main` build and deploy through GitHub Actions. In the repo's
Settings → Pages, set **Source** to **GitHub Actions**. The workflow sets
`url` and `baseurl` from Pages, so the same build works on
`<user>.github.io/personal` now and on a custom domain later.

## Content

Posts were migrated from WordPress (katieallred.com) via `wp2jekyll.py`.
Each post carries an explicit `permalink: /slug/` preserving its original
WordPress URL, plus `title`, `date`, `last_modified_at`, `author`,
`categories`, `tags`, `image` (featured image), `description`/`seo_title`
(from Rank Math where set), and `wordpress_id`. Media lives under
`assets/uploads/YYYY/MM/`; scheduled posts have `scheduled: true` and
future dates (Jekyll skips them until the date arrives — preview with
`--future`). A few images missing from the import are listed in
`assets/uploads/MISSING.md`.

Pages were exported from WordPress into `pages/`, each with an explicit
`permalink`. They use the `landing` layout (the content brings its own
eyebrow and H1) except `link-in-bio`, which uses `blank` (no header or
footer). The privacy policy, terms, disclaimer and affiliate disclosure
use the `legal` layout: write each section as a `##` heading in
markdown and the layout builds the numbered "On this page" list; set
`updated` (the date shown) and `summary` (the plain-English card) in
front matter. The Elementor inline styles were remapped to the design-system
tokens. The contact and Community Playbook forms are Tally embeds
(`_includes/tally.html`); responses and settings live in Tally.
