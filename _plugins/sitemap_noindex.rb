# Keep noindex pages out of /sitemap.xml.
#
# jekyll-sitemap lists every page and post unless its front matter says
# `sitemap: false`. A page marked `noindex: true` (see _includes/seo.html)
# shouldn't be offered to search engines either, so it gets
# `sitemap: false` automatically before the sitemap is generated.

Jekyll::Hooks.register :site, :post_read do |site|
  (site.pages + site.documents).each do |doc|
    doc.data["sitemap"] = false if doc.data["noindex"]
  end
end
