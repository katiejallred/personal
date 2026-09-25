# Maintaining the site

Working notes for Katie and Claude: how the site is put together and the
conventions to follow when editing it. `CLAUDE.md` loads this file. It is
excluded from the Jekyll build, but the repository is public, so keep
passwords, API keys and anything else private out of it.

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
_data/             navigation, social links (fixed order), hero links,
                   books, schema (facts for structured data)
_layouts/          default, page, post, home, landing, legal, blank
_includes/         header, footer, seo, faq, author-card, related-posts…
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

## SEO and answer engines

`_includes/seo.html` writes every page's `<title>`, meta description,
canonical URL, Open Graph and X card tags, and a JSON-LD graph that links
the page to Katie (`Person`), her business (`ProfessionalService`) and the
site (`WebSite`), plus `BlogPosting` and breadcrumbs on posts. The facts
behind it (bio, job title, topics, business address) live in
`_data/schema.yml`; keep them in step with the press kit.

Google matches Katie across the web through the Person's `sameAs` list:
the social links in `_config.yml` plus the author and publisher profiles
in `person.same_as` in `_data/schema.yml` (Amazon, Goodreads, B&H,
Substack). Add a profile there when she gets a new one. Each book in
`_data/books.yml` also carries its 13-digit `isbn` and, where it has one,
its `google_books` page.

Front matter it reads: `seo_title` (the full `<title>`), `description`
(write one for every page and new post, about 150 characters, otherwise
the first paragraph is used), `image` (share image, otherwise a generated
share card, see below), `schema_type` (`ProfilePage`, `ContactPage`, `CollectionPage`…),
`schema_books: true` (describe `_data/books.yml` as `Book`s), and
`noindex: true`. A page's `faq:` list of `q`/`a` pairs renders through
`{% include faq.html %}` and becomes `FAQPage` data, so questions shown on
the page and what search and AI engines read stay identical.

Pages and posts without an `image` get a 1200×630 Open Graph share card
drawn at build time by `_plugins/og_images.rb` and `scripts/og_image.py`:
the red hero ground and wave, the KA wordmark, the title in Bricolage
Grotesque, a post's category in Caveat, and Katie's headshot. The card text
is `og_title` if set, otherwise `seo_title` or `title` without the
"| Katie Allred" part; `og_kicker` overrides the category line. Cards are
cached in `.jekyll-cache/og-images` and served from `/assets/images/og/`.
Drawing them needs Python 3 with Pillow (`pip install pillow`; the Pages
workflow installs it); without it the build warns and pages fall back to
the headshot.

The favicon set (`favicon.ico`, `favicon.svg`, `apple-touch-icon.png`,
`assets/images/icon-192.png` and `icon-512.png`, used by `site.webmanifest`)
is the KA wordmark tile, linked from `_includes/favicons.html`. The files are
committed; to redraw them, run `python3 scripts/favicon.py` (needs
`pip install pillow fonttools brotli`).

`/llms.txt` is a plain-text summary of Katie, her key pages, books and
recent writing for AI assistants, built from the same data. `robots.txt`
blocks crawlers that only gather AI training data (GPTBot, ClaudeBot,
Google-Extended, CCBot…) and allows search engines and AI search bots
(Googlebot, Bingbot, OAI-SearchBot, Claude-SearchBot, PerplexityBot…), so
the site can still be found and cited.

`/sitemap.xml` is built by jekyll-sitemap and linked from `robots.txt`. It
lists every page and post with its `last_modified_at` date. Leave a page out
with `sitemap: false`; pages with `noindex: true` are left out automatically
(`_plugins/sitemap_noindex.rb`). Posts end with an author
card and up to three related posts from the same category.

## Deploying

Pushes to `main` build and deploy through GitHub Actions. In the repo's
Settings → Pages, set **Source** to **GitHub Actions**. The workflow sets
`url` and `baseurl` from Pages, so the same build works on
`<user>.github.io/personal` now and on a custom domain later. It always
builds with `https://`, even when Pages reports an `http://` origin; keep
**Enforce HTTPS** ticked in Settings → Pages so visitors land there too.

## Content

Posts were migrated from WordPress (katieallred.com) via `wp2jekyll.py`.
Each post carries an explicit `permalink: /slug/` preserving its original
WordPress URL, plus `title`, `date`, `last_modified_at`, `author`,
`categories`, `tags`, `image` (featured image), `description`/`seo_title`
(from Rank Math where set), and `wordpress_id`. Media lives under
`assets/uploads/YYYY/MM/`; scheduled posts have `scheduled: true` and
future dates (Jekyll skips them until the date arrives — preview with
`--future`).

Give every image alt text: `![What the image shows](/assets/uploads/...)` in
Markdown, and `featured_image_alt:` for a post's featured image (it also
becomes `og:image:alt`). Leave a featured image's alt empty only when it is
a title graphic that repeats the post title.

Keep uploads small: at most 1600 px wide, saved as JPEG (quality ~82) for
photos and screenshots, which is usually under 300 KB. Use PNG only for
graphics that need transparency. Images inside posts lazy-load
automatically (`_plugins/lazy_images.rb`).

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
