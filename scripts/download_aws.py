import os
import argparse
import logging
import requests
from pystac_client import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Switch to Microsoft Planetary Computer (100% Free, Public, and No 404s/403s!)
STAC_API_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
SAS_TOKEN_URL = "https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2"

def download_file(url, local_path):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192 * 1024): 
                f.write(chunk)
    return local_path

def get_sas_token():
    # Gets the free public access token for the Landsat bucket
    res = requests.get(SAS_TOKEN_URL)
    res.raise_for_status()
    return res.json()["token"]

def download_landsat_cloud(product_id, bands, start_date, end_date, output_path):
    logger.info(f"Connecting to Planetary Computer STAC API...")
    client = Client.open(STAC_API_URL)
    
    parts = product_id.split('_')
    path_row = parts[2]
    wrs_path = path_row[:3]
    wrs_row = path_row[3:]
    
    logger.info(f"Searching for Path {wrs_path}, Row {wrs_row} between {start_date} and {end_date}")
    
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
        logger.error("Could not find any real Landsat passes for this location and date range.")
        return
        
    item = items[0]  
    logger.info(f"Found real product: {item.id}")
    
    # Get the free access token for Azure Blob Storage
    logger.info("Generating free public access token...")
    sas_token = get_sas_token()
    
    os.makedirs(output_path, exist_ok=True)
    bands_to_find = [b.strip() for b in bands]
    
    for band in bands_to_find:
        band_suffix = f"_{band}.TIF".lower()
        asset_href = None
        
        # Search all assets for the one whose filename ends with our band (e.g. _SR_B2.TIF)
        for asset_key, asset in item.assets.items():
            if asset.href.lower().endswith(band_suffix):
                asset_href = asset.href
                break
                
        if asset_href:
            # The direct download URL is the asset link + the access token
            download_url = f"{asset_href}?{sas_token}"
            
            short_band = band.split('_')[-1]
            out_filename = f"{product_id}_{short_band}.TIF"
            local_path = os.path.join(output_path, out_filename)
            
            logger.info(f"Downloading {band} ...")
            try:
                download_file(download_url, local_path)
                logger.info(f"✅ Successfully saved to {local_path}")
            except Exception as e:
                logger.error(f"❌ Failed to download {band}: {e}")
        else:
            logger.warning(f"⚠️ Could not find asset for band {band}.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Landsat 9 data from the Cloud.')
    parser.add_argument('product_id', type=str)
    parser.add_argument('bands', type=str)
    parser.add_argument('start_date', type=str)
    parser.add_argument('end_date', type=str)
    parser.add_argument('output_path', type=str)
    parser.add_argument('--ee_project_id', type=str, default=None)

    args = parser.parse_args()
    download_landsat_cloud(args.product_id, args.bands.split(','), args.start_date, args.end_date, args.output_path)
