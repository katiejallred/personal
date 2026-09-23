---
layout: post
title: Subnetting Part 2 - Subnet Mask, Magic Number
date: '2011-05-06 18:50:00'
last_modified_at: '2011-05-06 18:50:00'
author: Katie Allred
permalink: /subnetting-part-2-subnet-mask-magic-number/
categories:
- Legacy
tags:
- tech tips
- networking
wordpress_id: 2639
---

|  |  |  |  |
| --- | --- | --- | --- |
| **Class** | **Host address range** | **Network address** | **Default mask** |
| A | 0.0.0.0 - 127.255.255.255 | x.0.0.0 | 255.0.0.0 |
| B | 128.0.0.0 - 191.255.255.255 | x.x.0.0 | 255.255.0.0 |
| C | 192.0.0.0 - 223.255.255.255 | x.x.x.0 | 255.255.255.0 |

(from http://compnetworking.about.com/od/workingwithipaddresses/l/aa042900a.htm)

Class D and any others are reserved or not really in use.

These are the general subnet masks for each IP address.

Now you want to get more specific.

You have an IP address of 192.16.32.0 (a class C address) and you want to get a subnet it for 8 subnets and 25 hosts. (Note: you will always want enough, or more than enough subnets or hosts, more is never bad)

Subnets (number of one's)  
2n  (The n here is denoting the number of one's needed in the last octet) = 2n = 23=  8 subnets

Hosts (number of zeros)  
2n -2 (The n here is denoting the number of zero's needed in the last octet) = 2n-2 = 25-2=  30 hosts

So from those two equations we see that we need 3 one's and 5 zeros to give us 11100000 in binary and if we convert that to decimal we get (128+64+32) = 224 so our subnet mask for 192.16.32.0 is

192.16.32.224

With that we can break our network into subnetworks. Just take 256 (256 is called the "magic" number, we always use it for the purpose of finding the steps between subnets) so  
256-224 = 32. So we now know that there is 32 steps between each network. So we can get the network addresses as follows:

(8 subnetworks)  
192.16.32.0  
192.16.32.32  
192.16.32.64  
192.16.32.96  
192.16.32.128  
192.16.32.160  
192.16.32.192  
192.16.32.224

Each of these are a network address. With these you can tell the range, network address, and broadcast address of any IP address that comes your way.

For example a router pulls up 192.16.32.37  
We as humans can see that that would fall on the table above between 32 and 64. Meaning that the network address of that IP is 192.16.32.32, the broadcast is 192.16.32.63 (64 is the network address of the next subnet), and the range would be 192.16.32.33 - 192.16.32.62.

CITER and more coming your way.

If you want to practice subnetting the best thing I've found is: <http://faculty.valleycollege.net/rpowell/jscript/subnet2.htm>  
It will automatically generate a problem and let you input the solution.

![](https://blogger.googleusercontent.com/tracker/8211801277441843385-6142576003824254073?l=katiejallred.blogspot.com)
