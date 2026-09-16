---
layout: post
title: "The Writing and Publishing Workflow"
date: 2026-08-20 09:30:00 -0500
categories: [meta]
tags: [workflow, writing]
excerpt: "How drafts, posts, and the local preview loop work in this Jekyll scaffold."
canonical_url: ""
featured_image: ""
slug: writing-and-publishing-workflow
---

New writing starts life in `_drafts/` as a file with no date in its name.
Preview drafts locally with:

```sh
bundle exec jekyll serve --drafts
```

When a draft is ready, move it into `_posts/` and rename it to
`YYYY-MM-DD-slug.md`. The permalink structure
(`/:year/:month/:day/:title/`) is derived from the date and slug, so imported
posts keep stable URLs as long as those two things are preserved.

Posts dated in the future are not published (`future: false`), which makes it
safe to stage scheduled content in `_posts/` ahead of time.
