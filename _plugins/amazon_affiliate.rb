# Amazon Associates links, handled once for the whole site.
#
# 1. Before rendering, flag any page or post whose source mentions Amazon
#    (amazon.com, amzn.to, or the book-card / amazon-url includes) with
#    `affiliate_links: true`. The layouts use that flag to show the
#    disclosure (_includes/affiliate-note.html). Set `affiliate_links: false`
#    in front matter to opt a page out.
# 2. After rendering, rewrite every Amazon link in the HTML so it carries
#    site.amazon.tag and rel="sponsored nofollow noopener". Product links
#    (/dp/ASIN, /gp/product/ASIN) become clean https://www.amazon.com/dp/ASIN/
#    URLs. amzn.to short links already carry the tag they were made with, so
#    only their rel changes.

module AmazonAffiliate
  MENTIONS = %r{amzn\.to/|amazon\.com/|include\s+(?:book-card|amazon-url)\.html}i
  ANCHOR = %r{<a\b[^>]*\bhref=(["'])(?:https?:)?//(?:www\.)?(?:amazon\.com|amzn\.to)/[^>]*>}i
  PRODUCT = %r{amazon\.com/(?:[^/?"']+/)?(?:dp|gp/product)/([A-Z0-9]{10})}i
  REL = %w[sponsored nofollow noopener].freeze

  module_function

  def tag(site)
    site.config.dig("amazon", "tag")
  end

  def rewrite_href(href, tag)
    return href if href.include?("amzn.to/")

    if (m = href.match(PRODUCT))
      return "https://www.amazon.com/dp/#{m[1].upcase}/?tag=#{tag}"
    end

    url = href.gsub("&amp;", "&").sub(/([?&])tag=[^&#]*&?/, '\1').sub(/[?&]\z/, "")
    sep = url.include?("?") ? "&" : "?"
    "#{url}#{sep}tag=#{tag}".gsub("&", "&amp;")
  end

  def rewrite_anchor(anchor, tag)
    anchor = anchor.sub(/\bhref=(["'])(.*?)\1/i) { "href=#{$1}#{rewrite_href($2, tag)}#{$1}" }
    if anchor =~ /\brel=(["'])(.*?)\1/i
      tokens = ($2.split + REL).uniq.join(" ")
      anchor.sub(/\brel=(["'])(.*?)\1/i, %(rel="#{tokens}"))
    else
      anchor.sub(/>\z/, %( rel="#{REL.join(' ')}">))
    end
  end
end

Jekyll::Hooks.register [:pages, :documents], :pre_render do |doc, payload|
  next if doc.data.key?("affiliate_links")
  next unless doc.content.to_s.match?(AmazonAffiliate::MENTIONS)

  doc.data["affiliate_links"] = true
  payload["page"]["affiliate_links"] = true if payload["page"].is_a?(Hash)
end

Jekyll::Hooks.register [:pages, :documents], :post_render do |doc|
  tag = AmazonAffiliate.tag(doc.site)
  next unless tag && doc.output_ext == ".html" && doc.output

  doc.output = doc.output.gsub(AmazonAffiliate::ANCHOR) do |anchor|
    AmazonAffiliate.rewrite_anchor(anchor, tag)
  end
end
