Run in python on a Macbook Pro with a 3.5 GHz Intel Core i7 (Hyperthreaded with 20 thread pool)

All renders done with 400x400 images in perspective without antialiasing
(Animation done with 256x256 images)

Scene                           | Time      | Primary Rays  | Shadow Rays   | Total Rays
---                             | ---:      | ---:          | ---:          | ---:
Animation (375 frames)          | ~25hrs    | 65,536/frame  | 65,536/frame  | 49,152,000
Texturing + CSG                 | 117.6s    | 160,000       | 160,000       | 320,000
