import folium
import base64
import os

cords = []
cords.append((6.1377549, -75.0355056, "Point 1"))
cords.append((6.1376056, -75.0354312, "Point 2"))
cords.append((6.1373799, -75.0356602, "Point 3"))
cords.append((6.1369349, -75.0357209, "Point 4"))
cords.append((6.1366899, -75.0351740, "Point 5"))
cords.append((6.1361038, -75.0349135, "Point 6"))
cords.append((6.1356305, -75.0352284, "Point 7"))
cords.append((6.1359625, -75.0356099, "Point 8"))
cords.append((6.1361638, -75.0359334, "Point 9"))
cords.append((6.1354545, -75.0361108, "Ultimate Point 10"))
cords.append((6.1352104, -75.0365886, "Point 11"))
cords.append((6.1344661, -75.0365822, "Point 12"))
cords.append((6.1344367, -75.0366828, "Point 13"))
cords.append((6.1337560, -75.0369242, "Point 14"))
cords.append((6.1336160, -75.0371109, "Point 15"))
cords.append((6.1337900, -75.0372732, "Point 16"))
cords.append((6.1348124, -75.0369966, "Point 17"))
cords.append((6.1368459, -75.0361896, "Point 18"))

images = {
    "Point 3": ["p3.jpeg", "p3_1.jpeg", "p3_2.jpeg"],
    "Point 4": "p4.jpeg",
    "Point 14": "p14.jpeg",
    "Point 15": "p15.jpeg",
    "Point 16": "p16.mp4",
    "Point 17": "p17.mp4",
    "Point 18": "p18.mp4",
}

# ---------------------------------------------------------------------------
# 1b. Media handling. Images and videos both supported.
#     EMBED=True bakes the media into the HTML as base64 -> one portable file,
#     but videos make it LARGE. Set EMBED=False to reference files by path
#     instead (then keep map.html sitting next to the media files).
# ---------------------------------------------------------------------------
EMBED = True
 
MIME = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
    ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime",
    ".m4v": "video/mp4", ".ogg": "video/ogg",
}
VIDEO_EXTS = {".mp4", ".webm", ".mov", ".m4v", ".ogg"}
 
 
def media_src(path):
    """URL/data URI -> unchanged. Local file -> base64 data URI if EMBED,
    else the plain path."""
    if path.startswith(("http://", "https://", "data:")):
        return path
    if not EMBED:
        return path
    ext = os.path.splitext(path)[1].lower()
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{MIME.get(ext, 'application/octet-stream')};base64,{b64}"
 
 
def media_html(path, width=220):
    """Return one <img> or <video> block depending on file type."""
    ext = os.path.splitext(path)[1].lower()
    src = media_src(path)
    if ext in VIDEO_EXTS:
        return (f'<video width="{width}" controls>'
                f'<source src="{src}" type="{MIME.get(ext, "video/mp4")}">'
                f'</video>')
    return f'<img src="{src}" width="{width}">'
 
 
def media_block(val, width=220):
    """Accept one path or a list of paths; stack them in a scrollable box."""
    paths = val if isinstance(val, list) else [val]
    inner = "<br>".join(media_html(p, width) for p in paths)
    return f'<div style="max-height:320px;overflow-y:auto">{inner}</div>'
 
 
# ---------------------------------------------------------------------------
# 2. Base map (tiles=None so no default layer competes with our own set).
# ---------------------------------------------------------------------------
lats = [c[0] for c in cords]
lons = [c[1] for c in cords]
center = [sum(lats) / len(lats), sum(lons) / len(lons)]
 
m = folium.Map(location=center, zoom_start=7, tiles=None)
 
# ---------------------------------------------------------------------------
# 3. Layers. Switch between these with the control in the top-right corner.
# ---------------------------------------------------------------------------
folium.TileLayer("OpenStreetMap", name="Street").add_to(m)
 
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
          "World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri World Imagery",
    name="Satellite",
).add_to(m)
 
folium.TileLayer(
    tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attr="OpenTopoMap (CC-BY-SA)",
    name="Topographic",
    max_zoom=17,
).add_to(m)
 
# ---------------------------------------------------------------------------
# 4. Pins. Labels present in `images` get their picture(s)/video(s) in the popup.
# ---------------------------------------------------------------------------
for lat, lon, label in cords:
    caption = f"{label}<br>({lat:.4f}, {lon:.4f})"
    if label in images:
        html = media_block(images[label]) + "<br>" + caption
        popup = folium.Popup(html, max_width=260)
    else:
        popup = folium.Popup(caption, max_width=260)
 
    folium.Marker(
        [lat, lon],
        popup=popup,
        tooltip=label,
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)
 
# ---------------------------------------------------------------------------
# 5. Single closed loop connecting the points in order, back to Point 1.
# ---------------------------------------------------------------------------
folium.PolyLine(
    [(lat, lon) for lat, lon, _ in cords] + [(cords[0][0], cords[0][1])],
    color="#d62728", weight=3, opacity=0.85,
).add_to(m)
 
# ---------------------------------------------------------------------------
# 6. Fit the view to all points + add the layer toggle, then save.
# ---------------------------------------------------------------------------
m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
folium.LayerControl(collapsed=False).add_to(m)
 
m.save("index.html")
print("Saved index.html")