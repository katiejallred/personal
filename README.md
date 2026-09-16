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
_config.yml        Site metadata, permalinks, plugins, build behavior
_layouts/          default, page, post, home
_includes/         header, footer, post-card, pagination
_posts/            Published posts (YYYY-MM-DD-slug.md)
_drafts/           Undated drafts, only built with --drafts
assets/css|js|images
index.html         Home page (paginated post list)
about.md           Static page example
archive.html       Posts grouped by year
tags.html          Posts grouped by tag
```

## Migrating content

Imported posts should carry the front matter shape demonstrated in
`_posts/2026-08-02-sample-imported-post.md` (title, date with offset,
categories, tags, excerpt, canonical_url, featured_image, slug). Permalinks
are `/:year/:month/:day/:title/`, so preserving the original date and slug
preserves the original URL. Media goes under `assets/images/`.
