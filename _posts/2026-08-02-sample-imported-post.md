---
layout: post
title: "Sample Imported Post"
date: 2026-08-02 12:00:00 -0500
categories: [tech, web]
tags: [jekyll, static-sites]
excerpt: "A reference post demonstrating the full front matter shape used for content migrated from the previous site."
canonical_url: ""
featured_image: ""
featured_image_alt: ""
slug: sample-imported-post
---

This post exists as a **migration reference**. Its front matter demonstrates every
field the import tooling should populate when bringing content over from the
existing site.

## Front matter contract

| Field            | Purpose                                                    |
|------------------|------------------------------------------------------------|
| `title`          | Post title (quoted, so punctuation is safe)                |
| `date`           | Original publish date with timezone offset                 |
| `categories`     | Broad grouping; drives archive/URL grouping if enabled     |
| `tags`           | Fine-grained topics for the tags page                      |
| `excerpt`        | Card/preview summary; overrides the auto-generated excerpt |
| `canonical_url`  | Set when the canonical version lives elsewhere             |
| `featured_image` | Path under `/assets/images/` once media is migrated        |
| `slug`           | Preserves the original URL slug regardless of filename     |

## Markdown feature check

Inline `code`, *emphasis*, **strong**, and [links](https://jekyllrb.com) all
render through kramdown with GFM input.

```ruby
# Fenced code blocks are highlighted by Rouge
def hello
  puts "Hello from the scaffold"
end
```

> Blockquotes work too, for pull-quotes migrated from the old site.
