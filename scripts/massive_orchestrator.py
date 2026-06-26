import os
import sys
import shutil
import subprocess

# Ensure Python can find our scripts folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from download_aws import download_landsat_cloud

def run_massive_orchestrator():
    print("🌍 Starting Headless Massive Dataset Orchestrator...")
    
    # 25 highly diverse global locations (avoiding pure ocean).
    # This will generate ~20,000 patches and take roughly 1 hour 15 mins to run.
    regions = [
        ("137", "042", "Guwahati, India (River/Urban)"),
        ("148", "039", "New Delhi, India (Dense Urban/Agriculture)"),
        ("146", "044", "Mumbai, India (Coastal/Urban)"),
        ("144", "049", "Chennai, India (Coastal/Urban)"),
        ("148", "047", "Bangalore, India (Urban/Lakes)"),
        ("014", "032", "New York, USA (Coastal/Urban)"),
        ("040", "036", "Los Angeles, USA (Coastal/Desert/Urban)"),
        ("119", "038", "Shanghai, China (Coastal/Urban)"),
        ("107", "035", "Tokyo, Japan (Coastal/Urban/Mountains)"),
        ("170", "055", "Cape Town, South Africa (Coastal/Mountain)"),
        ("233", "079", "Amazon Rainforest, Brazil (Dense Forest)"),
        ("180", "040", "Sahara Desert Edge, Egypt (Arid/Sand)"),
        ("175", "043", "Nairobi, Kenya (Savanna)"),
        ("192", "024", "Berlin, Germany (Urban/Forest)"),
        ("202", "024", "London, UK (Urban/River)"),
        ("045", "029", "Yellowstone, USA (Forest/Geothermal)"),
        ("164", "043", "Mount Kilimanjaro, Tanzania (Snow/Mountain)"),
        ("113", "050", "Bali, Indonesia (Island/Volcano)"),
        ("091", "086", "Great Barrier Reef Edge, Australia (Coast/Coral)"),
        ("022", "039", "Mississippi River Delta, USA (Wetlands)"),
        ("176", "039", "Dubai, UAE (Desert/Coastal)"),
        ("001", "072", "Andes Mountains, Chile (Snow/Rock)"),
        ("117", "044", "Taipei, Taiwan (Island/Urban)"),
        ("140", "041", "Kathmandu, Nepal (Himalayas)"),
        ("226", "071", "Rio de Janeiro, Brazil (Coastal/Forest)")
    ]
    
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    bands = ["SR_B2", "SR_B3", "SR_B4", "ST_B10"]
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, 'input')
    downscaled_dir = os.path.join(base_dir, 'output', 'downscaled_data')
    rgb_dir = os.path.join(base_dir, 'output', 'rgb_images')
    
    for count, (path, row, name) in enumerate(regions, start=1):
        print(f"\n=======================================================")
        print(f"🚀 Processing Region {count}/{len(regions)}: {name} (Path: {path}, Row: {row})")
        print(f"=======================================================")
        
        product_id = f"LC09_L2SP_{path}{row}_00000000_00000000_02_T1"
        output_path = os.path.join(input_dir, product_id)
        
        # 1. Download
        download_landsat_cloud(product_id, bands, start_date, end_date, output_path)
        
        # 2. Run driver.py
        driver_path = os.path.join(base_dir, 'driver.py')
        print("⚙️ Running driver.py to process patches...")
        subprocess.run(["python", driver_path], check=True)
        
        # 3. Clean up to save space!
        print("🧹 Cleaning up heavy raw files to save Kaggle disk space...")
        for folder in [input_dir, downscaled_dir, rgb_dir]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                
    print("\n✅ All regions processed! Your lightweight dataset is ready in output/patches/")

if __name__ == '__main__':
    run_massive_orchestrator()
