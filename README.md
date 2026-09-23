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
