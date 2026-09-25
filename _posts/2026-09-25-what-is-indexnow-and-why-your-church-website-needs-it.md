---
layout: post
title: What Is IndexNow and Why Your Church Website Needs It
date: '2026-09-25 08:00:00'
last_modified_at: '2026-09-25'
author: Katie Allred
permalink: /what-is-indexnow-and-why-your-church-website-needs-it/
description: "IndexNow tells Bing and other search engines the moment your church website changes. What it is, how to turn it on in WordPress, and what to ask your developer."
og_title: IndexNow for Church Websites
categories:
- Church Communications
tags:
- church website
- SEO
- WordPress
image: /assets/uploads/2026/09/indexnow-church-website-laptop-stained-glass.jpg
featured_image_alt: "A laptop showing a church events page on a wooden desk in a sunlit church office, beside a green banker's lamp and a stained-glass window"
faq:
  - q: "What is IndexNow?"
    a: "IndexNow is a free, open protocol that lets your website tell participating search engines the moment a page is added, updated, or removed, instead of waiting for their crawlers to find the change on their own."
  - q: "Which search engines use IndexNow?"
    a: "Microsoft Bing, Yandex, Naver, Seznam and Yep take part, and a URL submitted to one is shared with the others. Search tools that draw on Bing's index, like DuckDuckGo and Yahoo, benefit too. The current list is at indexnow.org."
  - q: "Does Google support IndexNow?"
    a: "No. Google has tested IndexNow but does not take part. Keep submitting your sitemap in Google Search Console and keep your Google Business Profile up to date. IndexNow covers the other engines, and it does no harm to Google."
  - q: "Is IndexNow free?"
    a: "Yes. The protocol is free, and the IndexNow feature in Rank Math is free. Microsoft also publishes a free IndexNow plugin for WordPress. Yoast includes it in Yoast SEO Premium."
  - q: "How do I know IndexNow is working on my church website?"
    a: "Add your site to Bing Webmaster Tools and open the IndexNow report. After you publish or update a page, the URL should appear there within a few minutes."
---

It's Thursday afternoon. The pastor just told you the fall festival moved from Saturday to Sunday afternoon. You update the events page, post it on Facebook, and breathe a sigh of relief.

Then Saturday morning, a family searches "fall festival near me," finds your church, and the search result still says Saturday. They show up to an empty parking lot.

That gap between *when you change your website* and *when search engines notice* is real, and it can be days or even weeks for a small church site. There's a simple, free fix for a big part of it. It's called IndexNow.

## What is IndexNow?

IndexNow is an open protocol, created by Microsoft Bing and Yandex in 2021, that lets your website tap search engines on the shoulder and say, "Hey, this page just changed. Come take a look."

Here's how search usually works. Search engines send out crawlers that wander the web and revisit pages whenever they get around to it. A church website that posts a few times a month isn't at the top of anyone's list. So your new sermon series page, your updated Christmas Eve times, or your brand-new "Plan Your Visit" page might sit there unnoticed for a while.

IndexNow flips that from **pull to push**. Instead of waiting to be found, your site sends a short note to the search engines every time you publish, update, or delete a page. Submit to one participating engine and it shares the news with all the others.

## Why should a church care?

Because your website is your front door, and people are searching for you right now.

When someone new moves to town, gets curious after a hard season, or wants to know what time Easter services start, they search. Remember, [your website is still your most important outreach tool](/why-your-church-website-is-still-your-most-important-outreach-tool/). But it only works if search engines are showing the current version of it.

IndexNow matters most when your information changes:

- **Service times** shift for summer, holidays, or weather.
- **Events** get added, moved, or canceled.
- **New pages** go up for sermon series, VBS, or a capital campaign.
- **Old pages** come down, and you don't want people landing on last year's VBS registration.

It also matters beyond traditional search. Microsoft Bing takes part in IndexNow, and Bing's index feeds other tools too. DuckDuckGo and Yahoo draw on it, and so do several AI assistants that search the web to answer people's questions. More and more people are asking an AI "Is there a church near me with a good kids' ministry?" You want the answer it finds to be accurate.

## What IndexNow does not do

Let's be clear so you know what you're getting.

**Google does not use IndexNow.** Google has tested it, but it isn't a participating search engine. For Google, keep your sitemap submitted in [Google Search Console](https://search.google.com/search-console) and keep your Google Business Profile updated. Those are still essential. IndexNow covers Bing and the rest, and it doesn't hurt anything with Google.

**It doesn't guarantee rankings.** IndexNow gets your pages *noticed* faster. It doesn't make them rank higher. Clear, helpful content still does the heavy lifting.

**It isn't a replacement for a good website.** If your service times are buried three clicks deep, IndexNow will just help search engines find that faster. Fix the content first.

## How to set up IndexNow in WordPress

Good news: if your church runs on WordPress, this is a ten-minute job, and you probably don't need to touch any code. The rule of thumb is simple. **Use one IndexNow tool, not two.** If you already have an SEO plugin, turn it on there.

First, check which SEO plugin you have. In your WordPress dashboard, go to **Plugins** and look for Rank Math, Yoast SEO, All in One SEO (AIOSEO), or SEOPress. Then follow the path that matches.

### If you use Rank Math (the easiest path)

Rank Math makes this easiest, because IndexNow is included in the free version.

1. Go to **Rank Math SEO → Dashboard**.
2. Find the **Instant Indexing** module and switch it on.
3. Go to **Rank Math SEO → Instant Indexing** and make sure your post types (posts, pages, events) are checked for automatic submission.

That's it. Rank Math creates the API key for you and pings IndexNow every time you publish or update something. You'll also find a tab there to submit URLs by hand if you ever need to.

### If you use Yoast SEO

IndexNow is part of **Yoast SEO Premium**. If you have Premium, it runs automatically in the background. If you're on the free version, don't install a second SEO plugin just for this. Use Microsoft's plugin below instead.

### If you use All in One SEO or SEOPress

Both offer IndexNow. Look in your plugin's settings or add-ons for "IndexNow," switch it on, and let it generate your key.

### If you don't use an SEO plugin

Install Microsoft's official **IndexNow** plugin:

1. Go to **Plugins → Add New** and search for "IndexNow."
2. Install and activate the plugin published by **Microsoft Bing**.
3. Open its settings. It generates your key and starts submitting automatically when you publish, update, or delete content.

### Check that it's working

Don't just set it and forget it. Take five more minutes to confirm.

1. Create a free account at [Bing Webmaster Tools](https://www.bing.com/webmasters) and add your church's website. (You can import it straight from Google Search Console if you already use it.)
2. Update a page on your site. Fixing a typo on your "Plan Your Visit" page works fine.
3. In Bing Webmaster Tools, open the **IndexNow** report. Within a few minutes, you should see that URL listed.

If you see it, you're done. Celebrate with a cup of coffee.

One more note: if your church website sits behind **Cloudflare**, it has a setting called **Crawler Hints** that sends IndexNow pings for you. That's fine to use, but pick one method so you're not doubling up.

## What to ask your web developer

Maybe you don't have the keys to the website. Maybe a volunteer built it, an agency manages it, or it runs on something other than WordPress. That's okay! You don't need to know how to set it up. You just need to know what to ask.

Copy this and send it:

> Hi! Could you set up IndexNow on our church website so Bing and the other participating search engines are notified automatically whenever we publish, update, or delete a page? Specifically:
>
> 1. Turn on IndexNow, using our SEO plugin or platform if it's built in, so we're not adding a plugin we don't need.
> 2. Host the IndexNow key file at the root of our domain.
> 3. Make sure it submits only pages that actually changed, not the whole site on every update.
> 4. Add our site to Bing Webmaster Tools, give me access too, and confirm submissions appear in the IndexNow report.
> 5. Confirm our sitemap is still submitted to Google Search Console, since Google doesn't use IndexNow.
>
> Thank you!

A few follow-up questions worth asking, too:

- **Who owns the Bing Webmaster Tools and Google Search Console accounts?** The answer should be *the church*, with a staff email, not a volunteer's personal account.
- **What happens when you're no longer our developer?** Make sure the setup keeps running without them.
- **Is our platform already doing this?** Some website builders and hosts, like Wix and Duda, have IndexNow built in. If yours does, great. Just confirm it's on.

A good developer will be glad you asked. This is a small request that shows you're thinking about stewardship, not just decoration.

## Start small, but start

I'll be honest. When I rebuilt this website, IndexNow was one of the first things I set up. Every time I publish or update a post, the search engines hear about it automatically. I don't have to think about it, and that's the whole point.

You're probably a team of one, or close to it. You don't need to become an SEO expert. You just need to take away one more reason that someone looking for a church home finds out-of-date information about yours.

So here's your next step: log in to WordPress this week, find your SEO plugin, and flip the switch. Or send that email to your developer. Ten minutes now can save a family from an empty parking lot later.

Jesus told us the harvest is plentiful (Matt 9:37). Some of that harvest is searching for you online tonight. Let's make sure they find the front door open.

If you'd like a second set of eyes on your church website, you can [book a time with me](https://meetwithkatie.com) or email me at [katie@katieallred.com](mailto:katie@katieallred.com).

## Frequently asked questions

<div class="faq">
{% include faq.html %}
</div>
