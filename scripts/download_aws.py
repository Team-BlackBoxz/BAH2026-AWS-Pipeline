import os
import argparse
import logging
import requests
from pystac_client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STAC_API_URL = "https://earth-search.aws.element84.com/v1"

def download_file(url, local_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192 * 1024): 
                f.write(chunk)
    return local_path

def download_landsat_aws(product_id, bands, start_date, end_date, output_path):
    logger.info(f"Connecting to AWS STAC API: {STAC_API_URL}")
    client = Client.open(STAC_API_URL)
    
    # Extract the Path and Row from the product ID string (e.g. 137042)
    parts = product_id.split('_')
    path_row = parts[2]
    wrs_path = path_row[:3]
    wrs_row = path_row[3:]
    
    logger.info(f"Searching AWS for Path {wrs_path}, Row {wrs_row} between {start_date} and {end_date}")
    
    # Search AWS for ANY valid satellite pass in that date range for that city
    search = client.search(
        collections=["landsat-c2-l2"],
        query={
            "landsat:wrs_path": {"eq": wrs_path},
            "landsat:wrs_row": {"eq": wrs_row}
        },
        datetime=f"{start_date}/{end_date}"
    )
    items = list(search.items())
    
    if not items:
        logger.error("Could not find any real Landsat passes on AWS for this location and date range.")
        return
        
    item = items[0]  # Grab the first real image found!
    logger.info(f"Found real product in AWS catalog: {item.id}")
    
    os.makedirs(output_path, exist_ok=True)
    bands_to_find = [b.strip() for b in bands]
    
    for band in bands_to_find:
        band_suffix = f"_{band}.TIF".lower()
        asset_href = None
        
        for asset_key, asset in item.assets.items():
            if asset.href.lower().endswith(band_suffix):
                asset_href = asset.href
                break
                
        if asset_href:
            short_band = band.split('_')[-1]
            out_filename = f"{product_id}_{short_band}.TIF"
            local_path = os.path.join(output_path, out_filename)
            
            # Convert the internal s3:// link to the completely public Google Cloud mirror!
            if asset_href.startswith("s3://usgs-landsat/"):
                asset_href = asset_href.replace("s3://usgs-landsat/", "https://storage.googleapis.com/gcp-public-data-landsat/")
            
            logger.info(f"Downloading {band} from {asset_href} ...")
            try:
                download_file(asset_href, local_path)
                logger.info(f"✅ Successfully saved to {local_path}")
            except Exception as e:
                logger.error(f"❌ Failed to download {band}: {e}")
        else:
            logger.warning(f"⚠️ Could not find a matching asset for band {band}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Landsat 9 data from AWS.')
    parser.add_argument('product_id', type=str)
    parser.add_argument('bands', type=str)
    parser.add_argument('start_date', type=str)
    parser.add_argument('end_date', type=str)
    parser.add_argument('output_path', type=str)
    parser.add_argument('--ee_project_id', type=str, default=None)

    args = parser.parse_args()
    download_landsat_aws(args.product_id, args.bands.split(','), args.start_date, args.end_date, args.output_path)
