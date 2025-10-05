# Quick script to convert
import rasterio as rio
import matplotlib.pyplot as plt
import numpy as np

with rio.open('outputs/ratio_post_nov2024.tif') as src:
    data = src.read(1)
    
plt.figure(figsize=(10, 8))
plt.imshow(data, cmap='RdYlGn', vmin=-25, vmax=-5)
plt.colorbar(label='VH/VV Ratio (dB)')
plt.title('Surface Classification via VH/VV Ratio')
plt.axis('off')
plt.tight_layout()
plt.savefig('outputs/ratio_map_display.png', dpi=150, bbox_inches='tight')
print("Saved ratio_map_display.png")