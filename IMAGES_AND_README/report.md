Run in python on a Macbook Pro with a 3.5 GHz Intel Core i7 (Hyperthreaded with 20 thread pool)

All renders done with 400x400 images in perspective without antialiasing

Scene                           | Time      | Primary Rays  | Shadow Rays   | Total Rays
---                             | ---:      | ---:          | ---:          | ---:
Area Light (16 samples)         | 1718s     | 160,000       | 2,707,595     | 2,867,595
Perfect Reflection              | 168.8s    | 163,941       | 156,059       | 320,000
Transparent Object (`n=3.0`)    | 222.1s    | 190,763       | 190,763       | 381,526