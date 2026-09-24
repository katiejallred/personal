# Open Graph share cards for pages and posts that have no image of their own.
#
# After the site is read, every HTML page or post without `image` or
# `featured_image` gets a 1200x630 card in the design system (title, the
# post's category, Katie's headshot), drawn by scripts/og_image.py. The PNGs
# are cached in .jekyll-cache/og-images and published at
# /assets/images/og/<title-slug>-<hash>.png, and the page's `og_image` is set
# so _includes/seo.html uses it. The hash covers the text and the script, so
# a new title or design gets a new URL and social networks refetch it.
#
# Front matter: `og_title` (card text; otherwise seo_title, then title,
# minus a leading or trailing "| Katie Allred") and
# `og_kicker` (the line above it; posts default to their first category).
# A non-breaking space ("\u00A0" in a double-quoted YAML string) keeps two
# words on the same line of the card.
# Set `og_images: false` in _config.yml to turn this off. Needs python3 with
# Pillow; without them the build warns and pages keep the headshot.

require "digest"
require "json"
require "open3"

module OgImages
  DIR = "assets/images/og"
  SCRIPT = "scripts/og_image.py"

  class Generator < Jekyll::Generator
    safe true
    priority :lowest # after jekyll-paginate adds its pages

    def generate(site)
      return if site.config["og_images"] == false

      script = site.in_source_dir(SCRIPT)
      version = Digest::SHA1.file(script).hexdigest
      cache = site.in_cache_dir("og-images")
      cards = {}
      pages = []

      (site.pages + site.posts.docs).each do |page|
        data = page.data
        next unless page.output_ext == ".html"
        next if data["image"] || data["featured_image"] || data["noindex"]

        post = page.is_a?(Jekyll::Document)
        title = data["og_title"] || (post ? data["title"] : data["seo_title"] || data["title"]) || site.config["title"]
        kicker = data["og_kicker"] || (post ? Array(data["categories"]).first : nil)
        title = strip_site_name(title.to_s, site.config["title"])
        kicker = kicker.to_s.strip

        hash = Digest::SHA1.hexdigest([version, title, kicker].join("\n"))[0, 8]
        slug = Jekyll::Utils.slugify(title)[0, 50].sub(/-+\z/, "")
        name = "#{slug}-#{hash}.png"
        cards[name] ||= { "title" => title, "kicker" => kicker, "out" => File.join(cache, DIR, name) }
        pages << [page, name]
      end

      missing = cards.values.reject { |card| File.exist?(card["out"]) }
      render(missing, script) unless missing.empty?

      drawn = cards.select { |_name, card| File.exist?(card["out"]) }
      drawn.each_key { |name| site.static_files << Jekyll::StaticFile.new(site, cache, DIR, name) }
      pages.each do |page, name|
        page.data["og_image"] = "/#{DIR}/#{name}" if drawn.key?(name)
      end
    end

    private

    # "Press Kit | Katie Allred" -> "Press Kit"; the card already shows the name.
    def strip_site_name(title, name)
      sep = /\s*[|\-\u2013\u2014]\s*/
      name = Regexp.escape(name.to_s)
      stripped = title.strip.sub(/#{sep}#{name}\z/, "").sub(/\A#{name}#{sep}/, "")
      stripped.empty? ? title.strip : stripped
    end

    def render(cards, script)
      Jekyll.logger.info "OG images:", "drawing #{cards.size} share card(s)"
      _out, err, status = Open3.capture3("python3", script, stdin_data: JSON.generate(cards))
      return if status.success?

      Jekyll.logger.warn "OG images:", "#{SCRIPT} failed; pages keep the default image"
      Jekyll.logger.warn "", err.lines.last.to_s.strip
    rescue Errno::ENOENT
      Jekyll.logger.warn "OG images:", "python3 not found; pages keep the default image"
    end
  end
end
