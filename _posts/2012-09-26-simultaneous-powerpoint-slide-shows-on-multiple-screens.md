---
layout: post
title: Simultaneous Powerpoint Slide Shows on Multiple Screens
date: '2012-09-26 14:20:24'
last_modified_at: '2026-09-25'
author: Katie Allred
permalink: /simultaneous-powerpoint-slide-shows-on-multiple-screens/
categories:
- AI & Tech
tags:
- tech tips
- Microsoft Office
wordpress_id: 307
description: "How to run two PowerPoint slideshows on two monitors at the same time without either pausing. No code or paid software needed."
faq:
  - q: "Can PowerPoint run two full-screen slideshows at the same time?"
    a: "Not both in full-screen mode. Set one deck to Presented by a speaker (full screen) and the other to Browsed by an individual (window), then maximize the windowed deck on the second monitor. Both will play at once."
  - q: "How do I show my notes on my laptop and the slides on the projector?"
    a: "Use Presenter View. Extend your displays, turn on Use Presenter View in the Slide Show tab, and PowerPoint shows your notes on your screen and the slides on the projector. Use Swap Displays if they appear on the wrong screens."
  - q: "How do I pick which monitor a PowerPoint slideshow plays on?"
    a: "On the Slide Show tab, use the Monitor setting to choose the display for the full-screen show. Make sure your displays are extended, not mirrored, first."
  - q: "How do I make a PowerPoint loop on a lobby screen?"
    a: "In Set Up Slide Show, check Loop continuously until Esc, then set automatic slide timings in the Transitions tab. Exporting the deck as a video and playing it on repeat is another reliable option."
---

*Updated September 2026 with current PowerPoint steps, Presenter View, other ways to run two screens, and answers to common questions.*

You will Google this to no avail and be angry that you did. After creating a batch file and using the RUNAS command in command prompt and after seriously considering dropping $100 for PowerShow, I HAVE FINALLY FIGURED IT OUT! And luckily, the solution is all in powerpoint, no programming or money involved.

This is how to run two different powerpoint slideshows on two different monitors at the same time (without either pausing!)

Open your first slideshow.

Click the Slide Show tab on the ribbon > Click Set Up Slideshow > Click Present by Speaker (Full Screen)

[![PowerPoint Slide Show tab with the Set Up Slide Show button](/assets/uploads/2012/09/powerpoint3.jpeg "powerpoint3")](/assets/uploads/2012/09/powerpoint3.jpeg)

Open your second slideshow. Drag it to the other window. Set that window in the Slide Show tab to "Show On" that monitor.

Click the Slide Show tab on the ribbon > Click Set Up Slideshow > Click Present by an Individual (Windows)

Now present both slideshows. They will work and show at the same time! We have one slideshow that has videos and the other is just a regular slideshow with no sound.

## Does this still work in 2026?

Yes. PowerPoint still only lets one slideshow take over a screen in full-screen mode at a time, so the trick above is still the way to run two decks at once without buying anything. The option names have shifted a little over the years. In current versions of PowerPoint, open the **Slide Show** tab, click **Set Up Slide Show**, and you'll see:

- **Presented by a speaker (full screen)** for your main deck
- **Browsed by an individual (window)** for your second deck

The windowed deck won't be perfectly edge to edge the way the full-screen one is, but once you maximize the window on the second display, most people in the room won't notice.

## Step by step with a current version of PowerPoint

1. **Extend your displays first.** On Windows, press Windows key + P and choose **Extend**. On a Mac, open System Settings, go to Displays, and make sure the screens are not mirrored.
2. **Open deck one.** In Set Up Slide Show, choose **Presented by a speaker (full screen)**. Use the **Monitor** setting on the Slide Show tab to pick the screen it should play on.
3. **Open deck two.** In Set Up Slide Show, choose **Browsed by an individual (window)**.
4. **Start deck two first.** Drag its window to the other display and maximize it.
5. **Start deck one.** It fills its assigned screen, and both keep running.
6. **Test with sound.** Only one deck should have audio, or you'll have two videos talking over each other.

If one deck is a loop, like announcements in a lobby, check **Loop continuously until 'Esc'** in Set Up Slide Show and set automatic slide timings in the **Transitions** tab so it advances on its own.

## When you only need one deck on two screens

A lot of people who find this post actually need something simpler: their notes on the laptop and the slides on the projector. That's **Presenter View**, and it's built into PowerPoint. Extend your displays, check **Use Presenter View** on the Slide Show tab, and PowerPoint puts the audience view on the second screen while you see your notes, a timer, and the next slide. If the screens come up backwards, use **Swap Displays** at the top of Presenter View.

## Other options worth knowing

- **Export one deck as a video.** Go to File > Export > Create a Video, then play the video full screen on the second display. For a looping lobby screen, this is often the most reliable setup because nothing can accidentally advance.
- **Use presentation software built for services.** If you're doing this at church every week, tools like ProPresenter are designed to send different content to different screens (lyrics to the room, a stage display for the band, and so on). It's paid software, but it's built for exactly this.
- **Use a separate computer.** Sometimes the easiest answer is a second laptop or a small streaming device on the lobby TV.

My recommendation: use the free PowerPoint trick when you need it occasionally, and move to purpose-built software if two screens are part of every weekend. Either way, run through the whole thing once before people walk in. A five-minute test saves a lot of stress.

## Frequently asked questions

<div class="faq">
{% include faq.html %}
</div>
