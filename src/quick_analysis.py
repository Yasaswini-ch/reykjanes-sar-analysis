import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# File paths
pre_vv = r"data\rtc\unknown\S1A_IW_20241118T185927_DVP_RTC30_G_gpufed_3E38\S1A_IW_20241118T185927_DVP_RTC30_G_gpufed_3E38_VV.tif"
pre_vh = r"data\rtc\unknown\S1A_IW_20241118T185927_DVP_RTC30_G_gpufed_3E38\S1A_IW_20241118T185927_DVP_RTC30_G_gpufed_3E38_VH.tif"
post_vv = r"data\rtc\unknown\S1A_IW_20250926T185918_DVR_RTC30_G_gpufed_92F9\S1A_IW_20250926T185918_DVR_RTC30_G_gpufed_92F9_VV.tif"
post_vh = r"data\rtc\unknown\S1A_IW_20250926T185918_DVR_RTC30_G_gpufed_92F9\S1A_IW_20250926T185918_DVR_RTC30_G_gpufed_92F9_VH.tif"

# Read data
print("Reading data...")
with rio.open(pre_vv) as src:
    vv1 = src.read(1).astype('float32')
    profile = src.profile

with rio.open(pre_vh) as src:
    vh1 = src.read(1).astype('float32')

with rio.open(post_vv) as src:
    vv2 = src.read(1).astype('float32')

with rio.open(post_vh) as src:
    vh2 = src.read(1).astype('float32')

print(f"Pre shape: {vv1.shape}, Post shape: {vv2.shape}")

# If shapes don't match, crop to smaller size
if vv1.shape != vv2.shape:
    print("Shapes don't match, cropping to common extent...")
    min_rows = min(vv1.shape[0], vv2.shape[0])
    min_cols = min(vv1.shape[1], vv2.shape[1])
    vv1 = vv1[:min_rows, :min_cols]
    vh1 = vh1[:min_rows, :min_cols]
    vv2 = vv2[:min_rows, :min_cols]
    vh2 = vh2[:min_rows, :min_cols]
    print(f"Cropped to: {vv1.shape}")

# Compute ratios
eps = 1e-6
ratio1 = 10 * np.log10((vh1 + eps) / (vv1 + eps))
ratio2 = 10 * np.log10((vh2 + eps) / (vv2 + eps))
delta = ratio2 - ratio1

# Save outputs
Path("outputs").mkdir(exist_ok=True)

profile.update(height=ratio1.shape[0], width=ratio1.shape[1], dtype='float32')
with rio.open('outputs/ratio_pre_20241118.tif', 'w', **profile) as dst:
    dst.write(ratio1, 1)

with rio.open('outputs/ratio_post_20250926.tif', 'w', **profile) as dst:
    dst.write(ratio2, 1)

with rio.open('outputs/delta_ratio.tif', 'w', **profile) as dst:
    dst.write(delta, 1)

print("Saved GeoTIFFs to outputs/")

# Create figure
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

im1 = axes[0].imshow(ratio1, cmap='RdYlGn', vmin=-25, vmax=-5)
axes[0].set_title('Nov 18, 2024 - VH/VV (dB)')
axes[0].axis('off')
plt.colorbar(im1, ax=axes[0])

im2 = axes[1].imshow(ratio2, cmap='RdYlGn', vmin=-25, vmax=-5)
axes[1].set_title('Sept 26, 2025 - VH/VV (dB)')
axes[1].axis('off')
plt.colorbar(im2, ax=axes[1])

im3 = axes[2].imshow(delta, cmap='RdBu_r', vmin=-5, vmax=5)
axes[2].set_title('Change (dB)')
axes[2].axis('off')
plt.colorbar(im3, ax=axes[2])

plt.tight_layout()
plt.savefig('outputs/comparison_nov2024_sept2025.png', dpi=150, bbox_inches='tight')
print("Saved figure to outputs/comparison_nov2024_sept2025.png")

# Statistics
print("\nStatistics:")
print(f"Pre ratio: mean={np.nanmean(ratio1):.2f}, std={np.nanstd(ratio1):.2f}")
print(f"Post ratio: mean={np.nanmean(ratio2):.2f}, std={np.nanstd(ratio2):.2f}")
print(f"Change: mean={np.nanmean(delta):.2f}, std={np.nanstd(delta):.2f}")
print(f"Max increase: {np.nanmax(delta):.2f} dB")
print(f"Max decrease: {np.nanmin(delta):.2f} dB")