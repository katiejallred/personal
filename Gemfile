source "https://rubygems.org"

# Core Jekyll. For classic GitHub Pages builds (gh-pages branch, no Actions),
# comment this out and uncomment the github-pages gem below instead.
gem "jekyll", "~> 4.3"

# gem "github-pages", group: :jekyll_plugins

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.17"
  gem "jekyll-sitemap", "~> 1.4"
  gem "jekyll-paginate", "~> 1.1"
end

# Ruby 3.4+ no longer bundles these standard libraries.
gem "csv"
gem "base64"
gem "bigdecimal"
gem "logger"

platforms :windows, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1", platforms: [:windows]
