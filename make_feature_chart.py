import struct, zlib

def write_png(filename, width, height, pixels):
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        raw.extend(pixels[y*stride:(y+1)*stride])
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    with open(filename, 'wb') as f:
        f.write(png)

# Draw an executive chart
w, h = 960, 540
# background #0B1120 -> R:11, G:17, B:32
img = bytearray([11, 17, 32, 255] * (w * h))

def fill_rect(x1, y1, x2, y2, r, g, b, a=255):
    for y in range(max(0, y1), min(h, y2)):
        idx = (y * w + max(0, x1)) * 4
        span = min(w, x2) - max(0, x1)
        if span > 0:
            img[idx : idx + span * 4] = bytearray([r, g, b, a] * span)

# Draw card container
fill_rect(40, 40, w - 40, h - 40, 19, 29, 49) # #131D31
# Border
fill_rect(40, 40, w - 40, 44, 35, 53, 78)
fill_rect(40, h - 44, w - 40, h - 40, 35, 53, 78)
fill_rect(40, 40, 44, h - 40, 35, 53, 78)
fill_rect(w - 44, 40, w - 40, h - 40, 35, 53, 78)

# Title accent bar
fill_rect(60, 60, 160, 66, 6, 182, 212) # cyan #06B6D4

# Left Section: Accuracy Comparison Bars
# Bar 1: Top-30 Hybrid (96.51%) -> Cyan #38BDF8
fill_rect(100, 200, 440, 240, 56, 189, 248)
# Bar 2: All-50 Features (96.45%) -> Cobalt #3B82F6
fill_rect(100, 280, 435, 320, 59, 130, 246)
# Bar 3: Top-20 Features (96.34%) -> Slate #64748B
fill_rect(100, 360, 420, 400, 100, 116, 139)

# Right Section: Latency Comparison (Lower is better)
# Top-30: 0.09 ms (Cyan, fast)
fill_rect(540, 200, 680, 240, 16, 185, 129) # Green #10B981 (Fastest 0.09 ms)
# All-50: 0.12 ms (Blue, 25% slower)
fill_rect(540, 280, 725, 320, 239, 68, 68) # Red/Amber (0.12 ms, +25% overhead)
# Top-20: 0.07 ms
fill_rect(540, 360, 650, 400, 6, 182, 212) # Cyan (0.07 ms)

write_png('research_paper/img_feature_tiers.png', w, h, img)
print('[+] Created img_feature_tiers.png')
