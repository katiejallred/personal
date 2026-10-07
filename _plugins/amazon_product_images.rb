# Amazon product thumbnails for posts that set `product_images: true`.
#
# Amazon Associates only allows product images that come from Amazon's API
# and load from Amazon's own image servers, so nothing is downloaded or
# stored in the repo. Before the build, scripts/amazon_products.py asks the
# Amazon Creators API for every ASIN those posts link and writes the image
# URLs to _data/amazon_products.json (gitignored; the Pages workflow runs the
# script with the API credential from the repository secrets).
#
# After a flagged page or post renders, each table cell or list item that
# starts with a link to an Amazon product (/dp/ASIN or /gp/product/ASIN) with
# an image in that file gets a small linked thumbnail in front of the link:
#
#   <td class="has-product-thumb">
#     <a class="product-thumb" href="…same link…" rel="sponsored nofollow noopener"
#        tabindex="-1" aria-hidden="true"><img src="https://m.media-amazon.com/…" …></a>
#     <a href="…">Product name</a>
#   </td>
#
# The thumbnail repeats the text link, so it is hidden from assistive
# technology and skipped by the keyboard, the same as the book-card cover.
# Its <img> carries width, height, srcset, sizes and loading="lazy" already,
# so the image_dimensions, responsive_images and lazy_images plugins leave it
# alone (they only handle local images anyway). Without the data file, or for
# an ASIN the API didn't return, the page renders exactly as before.

module AmazonProductImages
  DATA = "amazon_products"
  SIZES = "48px" # the thumbnail box in assets/css/main.css, minus its padding
  REL = "sponsored nofollow noopener"
  # <td> or <li> (optionally with attributes) whose content starts with an
  # Amazon product link. The href has already been given the affiliate tag
  # by _plugins/amazon_affiliate.rb, so it is copied as is.
  CELL = %r{
    <(td|li)\b([^>]*)>
    (\s*)
    (<a\b[^>]*\bhref=(["'])(?:https?:)?//(?:www\.)?amazon\.com/[^"']*\5[^>]*>)
  }xi
  PRODUCT = %r{amazon\.com/(?:[^/?"']+/)?(?:dp|gp/product)/([A-Z0-9]{10})}i

  module_function

  def products(site)
    data = site.data[DATA]
    data.is_a?(Hash) && !data.empty? ? data : nil
  end

  # Add the thumbnail to every matching cell in `html`; returns [html, count].
  def insert(html, products)
    count = 0
    output = html.gsub(CELL) do |cell|
      tag, attrs, space, anchor = Regexp.last_match.captures.values_at(0, 1, 2, 3)
      href = anchor[/\bhref=(["'])(.*?)\1/i, 2]
      asin = href && href[PRODUCT, 1]&.upcase
      product = asin && products[asin]
      thumb = product && thumbnail(product, href)
      next cell unless thumb

      count += 1
      "<#{tag}#{with_class(attrs, 'has-product-thumb')}>#{space}#{thumb}#{anchor}"
    end
    [output, count]
  end

  def thumbnail(product, href)
    images = product["images"]
    return nil unless images.is_a?(Hash)

    main = images["medium"] || images["small"] || images["large"]
    return nil unless main.is_a?(Hash) && main["url"]

    srcset = images.values
                   .select { |i| i.is_a?(Hash) && i["url"] && i["width"] }
                   .sort_by { |i| i["width"].to_i }
                   .map { |i| "#{i['url']} #{i['width']}w" }
                   .join(", ")
    img = %(<img src="#{main['url']}" alt="")
    img += %( width="#{main['width']}" height="#{main['height']}") if main["width"] && main["height"]
    img += %( srcset="#{srcset}" sizes="#{SIZES}") unless srcset.empty?
    img += %( loading="lazy" decoding="async">)
    %(<a class="product-thumb" href="#{href}" rel="#{REL}" tabindex="-1" aria-hidden="true">#{img}</a>)
  end

  def with_class(attrs, name)
    if attrs =~ /\bclass=(["'])(.*?)\1/i
      attrs.sub(/\bclass=(["'])(.*?)\1/i) { %(class="#{[$2.split, name].flatten.uniq.join(' ')}") }
    else
      %(#{attrs} class="#{name}")
    end
  end
end

Jekyll::Hooks.register [:pages, :documents], :post_render do |doc|
  next unless doc.data["product_images"] && doc.output_ext == ".html" && doc.output

  products = AmazonProductImages.products(doc.site)
  next unless products

  doc.output, count = AmazonProductImages.insert(doc.output, products)
  Jekyll.logger.debug "Amazon product images:", "#{count} thumbnail(s) in #{doc.relative_path}"
end
