# App icon

- **lift-icon.png** — Source image (1024×1024).
- **Lift.icns** — macOS app icon (used by py2app).

To regenerate `Lift.icns` after changing the PNG (macOS):

```bash
cd icon
rm -rf Lift.iconset && mkdir Lift.iconset
for size in 16 32 128 256 512; do
  sips -z $size $size lift-icon.png --out "Lift.iconset/icon_${size}x${size}.png"
  sips -z $((size*2)) $((size*2)) lift-icon.png --out "Lift.iconset/icon_${size}x${size}@2x.png"
done
sips -z 1024 1024 lift-icon.png --out "Lift.iconset/icon_512x512@2x.png"
iconutil -c icns Lift.iconset -o Lift.icns
```
