import ee
import geemap
import os
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_landsat_data(product_id, bands, start_date, end_date, output_path, ee_project_id=None):
    if ee_project_id:
        ee.Initialize(project=ee_project_id)
    else:
        ee.Initialize()

    # 1. Dynamically parse Guwahati Path 137, Row 42 out of the command argument
    parts = product_id.split('_')
    path_row = parts[2] 
    wrs_path = int(path_row[:3])
    wrs_row = int(path_row[3:])

    logger.info(f"Target locked: WRS Path {wrs_path}, Row {wrs_row} (Guwahati Region)")

    collection = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') \
        .filterDate(start_date, end_date) \
        .filterMetadata('WRS_PATH', 'equals', wrs_path) \
        .filterMetadata('WRS_ROW', 'equals', wrs_row) \
        .select(bands)

    image = collection.first()

    if image:
        logger.info(f'Orbital pass acquired. Downloading bands: {bands} to {output_path}')
        os.makedirs(output_path, exist_ok=True)
        filename_prefix = f'landsat9_{product_id}'

        try:
            target_template = os.path.join(output_path, f"{filename_prefix}.tif")
            
            # 2. The Guwahati Cookie Cutter
            guwahati_roi = ee.Geometry.BBox(91.56, 26.10, 91.86, 26.25)
            assam_metric_crs = "EPSG:32646"

            # 3. Let geemap do the heavy lifting safely
            geemap.ee_export_image(
                image, 
                target_template, 
                scale=30, 
                crs=assam_metric_crs, 
                region=guwahati_roi, 
                file_per_band=True
            )
            logger.info(f'★ VICTORY! Real satellite TIFFs successfully downloaded to: {output_path}')
        except Exception as e:
            logger.error(f"Export failed: {e}")
    else:
        logger.warning('No satellite pass found for that Path/Row and Date combo.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download Landsat 9 data.')
    parser.add_argument('product_id', type=str)
    parser.add_argument('bands', type=str)
    parser.add_argument('start_date', type=str)
    parser.add_argument('end_date', type=str)
    parser.add_argument('output_path', type=str)
    parser.add_argument('--ee_project_id', type=str, default=None)

    args = parser.parse_args()
    download_landsat_data(args.product_id, args.bands.split(','), args.start_date, args.end_date, args.output_path, args.ee_project_id)