# Deal cards: show a post's price tables as product cards.
#
# A deals post (`deal_cards: true` in front matter) writes each group of
# products as an ordinary Markdown table whose header has a "Sale price" and
# a "List price" column, the product link in the first column and one more
# column of notes ("What it is", "Best for", "What it fixes"):
#
#   | Product | Sale price | List price | What it is |
#   | --- | --- | --- | --- |
#   | [Name](https://www.amazon.com/dp/ASIN) | $9.44 | $20.99 | An everyday sunscreen |
#
# After the post renders, each such table becomes a list of cards, one per
# row: the product picture when _data/amazon_products.json has one for its
# ASIN (see _plugins/amazon_product_images.rb; the picture is served from
# Amazon's servers), the name as a heading linking to the product, the notes
# with their column heading as a label, the deal price beside the crossed-out
# list price with a percent-off badge, and a "Buy on Amazon" button. Tables
# without those two columns are left alone. The affiliate plugin still tags
# every link, so the cards carry the same hrefs and rel as the table did.
#
# The hook runs at high priority, before the thumbnail plugin, and the card
# markup starts each list item with a <div>, so no second thumbnail is added.

module DealCards
  TABLE = %r{<table>\s*<thead>(.*?)</thead>\s*<tbody>(.*?)</tbody>\s*</table>}mi
  ROW = %r{<tr>(.*?)</tr>}mi
  CELL = %r{<t[dh][^>]*>(.*?)</t[dh]>}mi
  HREF = %r{\bhref=(["'])(.*?)\1}i
  PRODUCT = %r{amazon\.com/(?:[^/?"']+/)?(?:dp|gp/product)/([A-Z0-9]{10})}i
  PRICE = /\$\s*([\d,]+(?:\.\d+)?)/
  SIZES = "(min-width: 640px) 120px, 88px"

  module_function

  def convert(html, products)
    count = 0
    output = html.gsub(TABLE) do |table|
      head, body = Regexp.last_match.captures
      headers = head.scan(CELL).flatten.map { |h| strip(h) }
      sale = headers.index { |h| h =~ /\bsale\b/i }
      list = headers.index { |h| h =~ /\blist\b/i }
      next table unless sale && list && headers.size >= 3

      name = 0
      note = (0...headers.size).find { |i| ![name, sale, list].include?(i) }
      cards = body.scan(ROW).map do |(row)|
        cells = row.scan(CELL).flatten
        next if cells.size < headers.size
        card(cells, name, sale, list, note, headers, products)
      end.compact
      next table if cards.empty?

      count += cards.size
      %(<ul class="deal-list">\n#{cards.join("\n")}\n</ul>)
    end
    [output, count]
  end

  def card(cells, name, sale, list, note, headers, products)
    link = cells[name]
    href = link[HREF, 2]
    return nil unless href # the first column must be the product link

    asin = href[PRODUCT, 1]&.upcase
    product = asin && products && products[asin]
    media = product && media_html(product, href)
    deal = money(cells[sale])
    was = money(cells[list])
    off = deal && was && was > deal ? ((1 - deal / was) * 100).round : nil

    out = +%(<li class="deal#{' has-media' if media}">)
    out << media.to_s
    out << %(<div class="deal-body">)
    out << %(<h3 class="deal-title">#{link}</h3>)
    if note && !strip(cells[note]).empty?
      out << %(<p class="deal-note"><span class="deal-label">#{strip(headers[note])}:</span> #{cells[note].strip}</p>)
    end
    out << %(<p class="deal-price"><span class="deal-now"><span class="deal-label">Deal price</span> <strong>#{cells[sale].strip}</strong></span>)
    out << %( <span class="deal-was"><span class="deal-label">List price</span> <s>#{cells[list].strip}</s></span>)
    out << %( <span class="deal-badge">#{off}% off</span>) if off && off >= 5
    out << %(</p>)
    out << %(<p class="deal-buy"><a class="btn btn-red btn-sm" href="#{href}">Buy on Amazon &rarr;</a></p>)
    out << %(</div></li>)
    out
  end

  def media_html(product, href)
    images = product["images"]
    return nil unless images.is_a?(Hash)

    main = images["large"] || images["medium"] || images["small"]
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
    %(<div class="deal-media"><a href="#{href}" tabindex="-1" aria-hidden="true">#{img}</a></div>)
  end

  def money(cell)
    m = strip(cell)[PRICE, 1]
    m && m.delete(",").to_f
  end

  def strip(html)
    html.to_s.gsub(/<[^>]+>/, "").gsub("&nbsp;", " ").strip
  end
end

Jekyll::Hooks.register [:pages, :documents], :post_render, priority: :high do |doc|
  next unless doc.data["deal_cards"] && doc.output_ext == ".html" && doc.output

  products = doc.site.data["amazon_products"]
  products = nil unless products.is_a?(Hash)
  doc.output, count = DealCards.convert(doc.output, products)
  Jekyll.logger.debug "Deal cards:", "#{count} card(s) in #{doc.relative_path}"
end
