---
layout: post
title: Subneting Part 1 - Binary/Decimal Conversion
date: '2011-05-06 18:29:00'
last_modified_at: '2011-05-06 18:29:00'
author: Katie Allred
permalink: /subneting-part-1-binarydecimal-conversion/
categories:
- AI & Tech
tags:
- tech tips
- networking
wordpress_id: 2638
description: "Before you learn subnetting, master binary to decimal conversion. Here's the simple bit-value method I use, with a worked example."
---

Before you even attempt subnetting please be overly confident in your ability to convert binary to decimal and vice versa. The easiest way I've found is this method.

[![](/assets/uploads/2012/08/coollogo_com-5101882.png "Binary Conversion")](/assets/uploads/2012/08/coollogo_com-5101882.png)

So you have the number 76 in decimal and you want it in binary, well binary is broken into 8 bits of ones and zeros. Each one or zero represents whether that number is turned on or not. The following numbers never change. The easiest way for me to remember these numbers is to just add 1+1=2, 2+2=4, 4+4=8, 8+8=16, 16+16=32, 32+32=64, 64+64-128

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
|  |  |  |  |  |  |  |  |

They always fall largest to smallest like above.

So you have the number 76 and you want it in binary. The easiest way to do this is look at the table above. Can you take 128 out of 76 (76-128)? No. That means there is a 0 in that bracket. You can follow along with the table below. Can you take 64 out of 76 (76-64)? Yes. So that number is turned on. 76-64=12.  
With twelve left over we continue down the number path. 12 out of 32 (12-32)? No. 12 out of 16 (12-16)? No.  12 out of 8 (12-8)? Yes. Which leaves us with 4 and the next would be 4-4, so yes. With a remainder of 0's.

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
| 0 | 1 | 0 | 0 | 1 | 1 | 0 | 0 |

Our final binary is 01001100.

Alright so say instead we have a binary number of 11110000 (NOTE: 4 one's, and 4 zero's to total 8 bits).  
Plug that number into our chart.

|  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
| 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |

Every number with a one is "turned on" so you just add those numbers together.

128+64+32+16 = 240. So our decimal version of 11110000 is 240!

A great place to practice is <http://acc6.its.brooklyn.cuny.edu/~gurwitz/core5/binquiz.html>

The quiz there automatically generates a random number and lets you input your answer and check if it's right!

Well, I hope this helps on your quest to figure out subnetting. The next part will be a little more indepth.

![](https://blogger.googleusercontent.com/tracker/8211801277441843385-900213475625247824?l=katiejallred.blogspot.com)
