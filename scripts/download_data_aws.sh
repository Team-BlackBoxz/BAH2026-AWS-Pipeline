#!/bin/bash
# Wrapper for the new AWS Open Data download script

echo "Starting AWS Landsat 9 data download..."

# The exact Product ID (Landsat Collection 2 Level 2)
PRODUCT_ID="LC09_L2SP_137042_20230505_20230507_02_T1"
BANDS="SR_B2,SR_B3,SR_B4,ST_B10"
OUTPUT_PATH="./input/${PRODUCT_ID}"

# Run the python script
python scripts/download_aws.py $PRODUCT_ID $BANDS "ignored" "ignored" $OUTPUT_PATH

echo "Download process complete!"
