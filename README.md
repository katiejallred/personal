# katieallred.com

Source for the personal website and blog of Katie Allred, community
strategist, AI educator and author. Visit the live site at
[katieallred.com](https://www.katieallred.com).

Built with [Jekyll](https://jekyllrb.com) and deployed to GitHub Pages with
GitHub Actions.

## Run it locally

```sh
bundle install
bundle exec jekyll serve   # http://127.0.0.1:4000
```

Share cards are drawn at build time and need Python 3 with Pillow
(`pip install pillow`). Without it the build still works and pages fall
back to a default image.

## Content

The writing, photos and book covers belong to Katie Allred and may not be
reused without permission. Links to Amazon are affiliate links: as an Amazon
Associate, Katie earns from qualifying purchases. Product pictures in posts
that set `product_images: true` come from the Amazon Product Advertising API
at build time (`scripts/amazon_products.py`) and load from Amazon's servers;
none are stored in this repository.

To get in touch, use the [contact page](https://www.katieallred.com/contact/).
