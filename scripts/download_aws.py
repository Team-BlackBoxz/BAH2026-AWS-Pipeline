import os
import argparse
import logging
import requests
from pystac_client import Client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Official AWS STAC Catalog for Landsat Collection 2
STAC_API_URL = "https://earth-search.aws.element84.com/v1"

def download_file(url, local_path):
    """Streams a large file over HTTP to disk."""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            # 8MB chunks for efficient large file streaming
            for chunk in r.iter_content(chunk_size=8192 * 1024): 
                f.write(chunk)
    return local_path

def download_landsat_aws(product_id, bands, output_path):
    logger.info(f"Connecting to AWS STAC API: {STAC_API_URL}")
    client = Client.open(STAC_API_URL)
    
    # Query for the exact product ID
    logger.info(f"Searching for Landsat 9 product: {product_id}")
    search = client.search(
        collections=["landsat-c2-l2"],
        ids=[product_id]
    )
    items = list(search.items())
    
    if not items:
        logger.error(f"Could not find product {product_id} in AWS Earth Search.")
        return
        
    item = items[0]
    logger.info(f"Found product in AWS catalog: {item.id}")
    
    os.makedirs(output_path, exist_ok=True)
    
    # Map requested bands (e.g., 'SR_B2') to find the matching assets
    bands_to_find = [b.strip() for b in bands]
    
    for band in bands_to_find:
        # We look for the exact band suffix in the asset URL
        band_suffix = f"_{band}.TIF".lower()
        asset_href = None
        
        for asset_key, asset in item.assets.items():
            if asset.href.lower().endswith(band_suffix):
                asset_href = asset.href
                break
                
        if asset_href:
            # driver.py expects the format to be: <product_id>_B2.TIF
            # We will extract just the B2 or B10 part from SR_B2 to match the baseline
            short_band = band.split('_')[-1]
            out_filename = f"{product_id}_{short_band}.TIF"
            local_path = os.path.join(output_path, out_filename)
            
            logger.info(f"Downloading {band} from {asset_href} ...")
            try:
                download_file(asset_href, local_path)
                logger.info(f"✅ Successfully saved to {local_path}")
            except Exception as e:
                logger.error(f"❌ Failed to download {band}: {e}")
        else:
            logger.warning(f"⚠️ Could not find a matching asset for band {band} in this STAC item.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Landsat 9 data from AWS Open Data (No Authentication Required).')
    parser.add_argument('product_id', type=str, help='Unique ID for the product (e.g. LC09_L2SP_137042_20230505_20230507_02_T1).')
    parser.add_argument('bands', type=str, help='Comma-separated list of bands (e.g., SR_B2,SR_B3,SR_B4,ST_B10).')
    # The bash script passes start and end dates. AWS API doesn't need them if we have the exact ID, 
    # but we accept them to ensure compatibility with existing bash scripts.
    parser.add_argument('start_date', type=str, help='Start date (Ignored, kept for backward compatibility).', nargs='?')
    parser.add_argument('end_date', type=str, help='End date (Ignored, kept for backward compatibility).', nargs='?')
    parser.add_argument('output_path', type=str, help='Local path to save downloaded bands.')
    
    # Catch any leftover --ee_project_id flags so the script doesn't crash
    parser.add_argument('--ee_project_id', type=str, default=None, help='Ignored. AWS does not require Google Cloud Auth.')

    args = parser.parse_args()

    bands_list = args.bands.split(',')
    download_landsat_aws(args.product_id, bands_list, args.output_path)
