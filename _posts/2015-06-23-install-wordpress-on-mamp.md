---
layout: post
title: The Quick and Easy Way to Install Wordpress on MAMP
date: '2015-06-23 20:33:50'
last_modified_at: '2026-09-25'
author: Katie Allred
permalink: /install-wordpress-on-mamp/
categories:
- AI & Tech
tags:
- web design
- WordPress
- tech tips
- local development
wordpress_id: 1226
description: "Install WordPress on MAMP in under five minutes with a free shell script. Answer a few quick prompts and it does the rest, so local setup stops eating your day."
seo_title: Quickly Install Wordpress on MAMP
image: /assets/uploads/2015/06/Wordpress-MAMP.png
faq:
  - q: "Is MAMP still a good way to run WordPress locally?"
    a: "MAMP still works and is free, but for most people I recommend Local, a free app built specifically for WordPress that sets up the site, database, and server in a few clicks."
  - q: "What is the fastest way to install WordPress on MAMP?"
    a: "Use WP-CLI. With MAMP running, the commands wp core download, wp config create, wp db create, and wp core install set up a new WordPress site in a couple of minutes."
  - q: "What are MAMP's default database settings?"
    a: "By default, MAMP uses root as both the MySQL username and password, port 8889 for MySQL, and port 8888 for Apache. You can change the ports in MAMP's settings."
  - q: "Can I try WordPress without installing anything?"
    a: "Yes. WordPress Playground runs WordPress in your web browser. It is great for testing themes and plugins, but it is a temporary sandbox, not a place to build a real site."
---

*Updated September 2026 with what changed, easier tools like Local and WP-CLI, step-by-step setup, and answers to common questions.*

Are you using [MAMP](https://www.mamp.info/en/)? If you're like me, then you love MAMP. It's an easy solution for getting a local server development set up in a flash. If you are like me though, you hate to install [Wordpress](http://www.wordpress.org) on MAMP.

It's not that it's that complicated. It's just time consuming. You have time to be spending elsewhere, I completely agree.

Well, I finally found a script that will do this all for me and all I have to answer are some quick little prompts.

### Install Wordpress on MAMP in under 5 minutes.

[Click here](https://github.com/logoscreative/new-wp-mamp-shell) to see this script on Github or use the form below to download it now.

This was created by the good folks (ok, I'm pretty sure he's just one guy, but still) at [Logos Creative](http://logoscreative.co/).

## Bonus Content:

[Download this shell script now.](https://www.dropbox.com/s/ygqwwgjez9ob700/wp_sh.zip?dl=0)

Note: This shell script is contained within a zip file. You will need to unzip it. Then follow the instructions found on this [github page](https://github.com/logoscreative/new-wp-mamp-shell). This specific script has removed localhost:8888 and replaced it with just localhost.

**How do I run a shell script?**

Open Terminal. (Type Terminal into spotlight)

Locate your file. (In Terminal, type "cd folder-of-file", for example, mine is in Dropbox. So I would type: cd dropbox)

Run the file. (In Terminal, type: sh wp.sh)

Need more help? I'm only a [tweet](http://www.twitter.com/katiejallred) away!

## What I'd tell you in 2026

I wrote this in 2015, and a lot has changed in local WordPress development. The script above hasn't been updated in years, so treat it as a piece of history rather than something to rely on. The download link may not work anymore, and a script written for 2015 versions of MAMP and WordPress may not play nicely with today's. MAMP itself is still around and still works, but it's no longer the only easy option. Here's what I'd point you to now.

## Easier ways to run WordPress locally

- **Local.** [Local](https://localwp.com/) is a free app for Mac, Windows, and Linux built specifically for WordPress. You click to create a site, give it a name, and it sets up WordPress, the database, and the server for you. For most people, this is what I recommend today. It's the closest thing to "answer a few prompts and it does the rest" that this post was chasing.
- **WordPress Studio.** A free desktop app from the WordPress.com team that spins up local WordPress sites quickly. Worth a look if you want something lightweight.
- **WordPress Playground.** [WordPress Playground](https://playground.wordpress.net/) runs WordPress right in your browser with nothing to install. It's perfect for testing a theme or plugin for a few minutes. Just remember it's a sandbox, not a place to build a real site.
- **MAMP.** Still a solid choice if you already use it or need a general PHP and MySQL environment for more than WordPress.

## If you still love MAMP: use WP-CLI

The modern version of "a script that installs WordPress for me" is [WP-CLI](https://wp-cli.org/), the official command-line tool for WordPress. Once it's installed, setting up a new site on MAMP takes a few commands.

1. Start MAMP and make sure the Apache and MySQL servers are running.
2. In Terminal, `cd` into a new folder inside your MAMP document root (by default, the `htdocs` folder in your MAMP folder).
3. Run `wp core download` to download WordPress.
4. Run `wp config create --dbname=mysite --dbuser=root --dbpass=root --dbhost=127.0.0.1:8889` to create your config file. MAMP's default database username and password are both `root`, and its default MySQL port is 8889. Change these if you've changed MAMP's settings.
5. Run `wp db create` to create the database.
6. Run `wp core install --url=http://localhost:8888/mysite --title="My Site" --admin_user=yourname --admin_email=you@example.com` and WP-CLI will generate an admin password for you.

If you changed MAMP to use the standard ports (like the version of the script above did), drop the `:8888` from the URL and use your MySQL port in the `dbhost` setting. If a command complains about PHP or MySQL, make sure the PHP your Terminal is using is one that can reach MAMP's database.

## Which should you choose?

If you're a designer or church communicator who just needs a safe place to build and test a site, use Local. If you're a developer who wants control and repeatability, learn WP-CLI. It works with MAMP, Local, and your live host, and you'll use it for years. If you're just starting out with WordPress, I also wrote about [how to start a blog](/how-to-start-an-awesome-blog-in-4-easy-steps/).

Local development used to eat an afternoon. Now it takes a few minutes, which means more time for the part that matters: building something that helps people.

## Frequently asked questions

<div class="faq">
{% include faq.html %}
</div>
