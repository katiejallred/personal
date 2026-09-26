# Add width and height to local images so the browser can reserve their
# space before they load (no layout shift, better CLS).
#
# Markdown images render as plain <img src="…" alt="…"> with no size. After
# each page or post renders, look up every local image that has no width or
# height attribute, read its pixel size from the file header, and add both.
# The stylesheet's `img { max-width: 100%; height: auto; }` still scales the
# image to fit; the attributes only give the browser its aspect ratio early.
# CSS that sets its own aspect-ratio (book covers, cards) keeps winning.
#
# Reads PNG, JPEG, GIF and WebP headers in plain Ruby, so no gems are needed.
# SVGs, remote images and anything it can't read are left alone.

module ImageDimensions
  CACHE = {}

  module_function

  def size_of(path)
    CACHE.fetch(path) do
      CACHE[path] = begin
        File.open(path, "rb") { |f| read(f) }
      rescue StandardError
        nil
      end
    end
  end

  def read(f)
    head = f.read(32) || ""
    if head.start_with?("\x89PNG".b)
      head[16, 8].unpack("NN")
    elsif head.start_with?("GIF8")
      head[6, 4].unpack("vv")
    elsif head.start_with?("\xFF\xD8".b)
      jpeg(f)
    elsif head[0, 4] == "RIFF" && head[8, 4] == "WEBP"
      webp(head, f)
    end
  end

  # Walk the JPEG markers until a start-of-frame (SOFn) segment.
  def jpeg(f)
    f.seek(2)
    loop do
      marker = f.read(2)
      return nil unless marker && marker.getbyte(0) == 0xFF
      code = marker.getbyte(1)
      length = f.read(2).unpack1("n")
      if [0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF].include?(code)
        h, w = f.read(5).unpack("xnn")
        return orientation_swapped?(f) ? [h, w] : [w, h]
      end
      f.seek(length - 2, IO::SEEK_CUR)
    end
  end

  # EXIF orientations 5–8 are rotated 90°, so the displayed size is swapped.
  def orientation_swapped?(f)
    f.rewind
    data = f.read(65_536) || ""
    i = data.index("Exif\x00\x00".b)
    return false unless i
    tiff = i + 6
    big = data[tiff, 2] == "MM"
    u16 = big ? "n" : "v"
    u32 = big ? "N" : "V"
    ifd = tiff + data[tiff + 4, 4].unpack1(u32)
    count = data[ifd, 2].unpack1(u16)
    count.times do |n|
      entry = ifd + 2 + n * 12
      next unless data[entry, 2].unpack1(u16) == 0x0112
      return (5..8).cover?(data[entry + 8, 2].unpack1(u16))
    end
    false
  rescue StandardError
    false
  end

  def webp(head, f)
    case head[12, 4]
    when "VP8 "
      f.seek(26)
      w, h = f.read(4).unpack("vv")
      [w & 0x3FFF, h & 0x3FFF]
    when "VP8L"
      b = head[21, 4].unpack1("V")
      [(b & 0x3FFF) + 1, ((b >> 14) & 0x3FFF) + 1]
    when "VP8X"
      w = head[24, 3].bytes.each_with_index.sum { |byte, k| byte << (8 * k) }
      h = (f.read(3) || "").bytes.each_with_index.sum { |byte, k| byte << (8 * k) }
      [w + 1, h + 1]
    end
  end

  # Map an <img src> to a file in the site source, or nil if it isn't local.
  def local_file(src, site)
    path = src.sub(/[?#].*\z/, "")
    url = site.config["url"].to_s
    path = path.delete_prefix(url) unless url.empty?
    return nil unless path.start_with?("/") && !path.start_with?("//")
    baseurl = site.config["baseurl"].to_s
    path = path.delete_prefix(baseurl) unless baseurl.empty?
    return nil if path.end_with?(".svg")
    [site.source, site.dest].map { |root| File.join(root, path) }.find { |f| File.file?(f) }
  end
end

Jekyll::Hooks.register [:pages, :documents], :post_render do |doc|
  next unless doc.output_ext == ".html" && doc.output

  site = doc.site
  doc.output = doc.output.gsub(/<img\b[^>]*>/i) do |tag|
    next tag if tag =~ /\s(?:width|height)=/i
    src = tag[/\ssrc="([^"]+)"/i, 1]
    file = src && ImageDimensions.local_file(src, site)
    size = file && ImageDimensions.size_of(file)
    next tag unless size && size.all? { |n| n.to_i.positive? }
    tag.sub(/<img\b/i, %(<img width="#{size[0]}" height="#{size[1]}"))
  end
end
