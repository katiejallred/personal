# Lazy-load images inside blog posts.
#
# Markdown images render as plain <img> tags, so a long post (the Divi
# roundups have 10+ screenshots) downloads every image up front. After a
# post renders, add loading="lazy" decoding="async" to each <img> that
# doesn't already set loading or fetchpriority (the featured image at the
# top of post.html uses fetchpriority="high" and must load right away).

Jekyll::Hooks.register :posts, :post_render do |post|
  next unless post.output_ext == ".html" && post.output

  post.output = post.output.gsub(/<img\b(?![^>]*\b(?:loading|fetchpriority)=)/i,
                                 '<img loading="lazy" decoding="async"')
end
