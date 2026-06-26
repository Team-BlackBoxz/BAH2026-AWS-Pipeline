#!/bin/bash
echo "Starting AWS Landsat 9 data download..."

PRODUCT_ID="LC09_L2SP_137042_20230505_20230507_02_T1"
BANDS="SR_B2,SR_B3,SR_B4,ST_B10"
OUTPUT_PATH="./input/${PRODUCT_ID}"
START_DATE="2023-01-01"
END_DATE="2023-12-31"

python scripts/download_aws.py $PRODUCT_ID $BANDS $START_DATE $END_DATE $OUTPUT_PATH
echo "Download process complete!"
