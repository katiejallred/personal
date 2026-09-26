# Responsive images: smaller copies of each large site image, offered to the
# browser with srcset so phones don't download the full-size file.
#
# After the site is read, every JPEG, PNG or WebP under assets/uploads and
# assets/images that is wider than about 380px gets copies 320, 640, 960,
# 1280 and 1600px wide (each one narrower than the original), drawn by
# scripts/resize_images.py. A copy that isn't at least 10% smaller than the
# original (in bytes) is left out. The copies are cached in
# .jekyll-cache/responsive-images and published at
# /assets/images/resized/<name>-<hash>-<width>.<ext>; the hash covers the
# image and the script, so a replaced image gets new URLs.
#
# After each page or post renders, every <img> that points at one of those
# images gets `srcset` (the copies plus the original) and, when the template
# didn't set one, a default `sizes` for images in the article column.
# Templates that show an image at another width set their own `sizes`.
#
# Set `responsive_images: false` in _config.yml to turn this off. Needs
# python3 with Pillow; without them the build warns and images keep a plain
# src, exactly as before.

require "digest"
require "json"
require "open3"

module ResponsiveImages
  DIR = "assets/images/resized"
  SCRIPT = "scripts/resize_images.py"
  WIDTHS = [320, 640, 960, 1280, 1600].freeze
  SOURCES = %r{\A/assets/(?:uploads|images)/}.freeze
  SKIP = %r{\A/assets/images/(?:og|resized)/|/icon-\d+\.png\z}.freeze
  EXTENSIONS = %w[.jpg .jpeg .png .webp].freeze
  # The article column: full width on phones, 936px at most on desktop.
  DEFAULT_SIZES = "(min-width: 1000px) 936px, calc(100vw - 32px)"

  # "/assets/uploads/2026/09/photo.jpg" => [["/assets/images/resized/…-320.jpg", 320], …]
  SRCSETS = {}

  class Generator < Jekyll::Generator
    safe true
    priority :low

    def generate(site)
      SRCSETS.clear
      return if site.config["responsive_images"] == false

      script = site.in_source_dir(SCRIPT)
      version = Digest::SHA1.file(script).hexdigest
      cache = site.in_cache_dir("responsive-images")
      planned = {}
      jobs = []

      site.static_files.each do |file|
        url = file.url
        next unless url.match?(SOURCES) && !url.match?(SKIP)
        next unless EXTENSIONS.include?(File.extname(url).downcase)

        size = ImageDimensions.size_of(file.path)
        next unless size

        widths = WIDTHS.select { |w| w <= size[0] * 0.85 }
        next if widths.empty?

        hash = Digest::SHA1.hexdigest(version + Digest::SHA1.file(file.path).hexdigest)[0, 8]
        stem = url.delete_prefix("/assets/").sub(/\.[^.\/]+\z/, "").tr("/", "-")[0, 80]
        ext = File.extname(url).downcase
        copies = widths.map { |w| ["#{stem}-#{hash}-#{w}#{ext}", w] }
        copies.each do |name, w|
          out = File.join(cache, DIR, name)
          jobs << { "src" => file.path, "out" => out, "width" => w } unless File.exist?(out)
        end
        planned[url] = [copies, size[0], File.size(file.path)]
      end

      render(jobs, script) unless jobs.empty?

      planned.each do |url, (copies, original_width, original_bytes)|
        # Keep a copy only if it exists and is clearly smaller than the
        # original (some already-small PNGs grow when resized).
        made = copies.select do |name, _w|
          out = File.join(cache, DIR, name)
          File.exist?(out) && File.size(out) < original_bytes * 0.9
        end
        next if made.empty?

        made.each { |name, _w| site.static_files << Jekyll::StaticFile.new(site, cache, DIR, name) }
        SRCSETS[url] = made.map { |name, w| ["/#{DIR}/#{name}", w] } + [[url, original_width]]
      end
    end

    private

    def render(jobs, script)
      Jekyll.logger.info "Responsive images:", "resizing #{jobs.size} image cop#{jobs.size == 1 ? 'y' : 'ies'}"
      _out, err, status = Open3.capture3("python3", script, stdin_data: JSON.generate(jobs))
      return if status.success?

      Jekyll.logger.warn "Responsive images:", "#{SCRIPT} failed for some images; those keep a plain src"
      Jekyll.logger.warn "", err.lines.last.to_s.strip
    rescue Errno::ENOENT
      Jekyll.logger.warn "Responsive images:", "python3 not found; images keep a plain src"
    end
  end

  module_function

  # "/personal/assets/x.jpg" or "https://site/assets/x.jpg" => ["/assets/x.jpg", "/personal"]
  def split(src, site)
    path = src.sub(/[?#].*\z/, "")
    url = site.config["url"].to_s
    prefix = ""
    if !url.empty? && path.start_with?(url)
      path = path.delete_prefix(url)
      prefix = url
    end
    baseurl = site.config["baseurl"].to_s
    if !baseurl.empty? && path.start_with?(baseurl + "/")
      path = path.delete_prefix(baseurl)
      prefix += baseurl
    end
    [path, prefix]
  end
end

Jekyll::Hooks.register [:pages, :documents], :post_render do |doc|
  next unless doc.output_ext == ".html" && doc.output && !ResponsiveImages::SRCSETS.empty?

  site = doc.site
  doc.output = doc.output.gsub(/<img\b[^>]*>/i) do |tag|
    next tag if tag =~ /\ssrcset=/i
    src = tag[/\ssrc="([^"]+)"/i, 1]
    next tag unless src
    path, prefix = ResponsiveImages.split(src, site)
    copies = ResponsiveImages::SRCSETS[path]
    next tag unless copies
    srcset = copies.map { |url, w| "#{prefix}#{url} #{w}w" }.join(", ")
    attrs = %( srcset="#{srcset}")
    attrs += %( sizes="#{ResponsiveImages::DEFAULT_SIZES}") unless tag =~ /\ssizes=/i
    tag.sub(/<img\b/i, "<img#{attrs}")
  end
end
