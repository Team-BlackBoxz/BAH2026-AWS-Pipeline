import os
import sys
import shutil
import subprocess

# Ensure Python can find our scripts folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from download_aws import download_landsat_cloud

def run_massive_orchestrator():
    print("🌍 Starting Headless Massive Dataset Orchestrator...")
    
    # If your run crashed, you can change this number to resume where you left off!
    # (e.g., if it crashed on region 18, set START_INDEX = 18)
    START_INDEX = 1
    
    # 25 highly diverse global locations (avoiding pure ocean).
    # This will generate ~20,000 patches and take roughly 1 hour 15 mins to run.
    regions = [
        # 🇮🇳 Indian Cities (Focusing on local accuracy)
        ("137", "042", "Guwahati (River/Urban)"),
        ("148", "039", "New Delhi (Dense Urban/Pollution)"),
        ("146", "044", "Mumbai (Coastal/Urban)"),
        ("144", "049", "Chennai (Coastal/Tropical)"),
        ("148", "047", "Bangalore (Urban/Vegetation)"),
        
        # 🏙️ Dense Global Urban Metropolises
        ("014", "032", "New York City, USA (Concrete Jungle)"),
        ("040", "036", "Los Angeles, USA (Sprawl/Desert)"),
        ("119", "038", "Shanghai, China (Massive Density)"),
        ("107", "035", "Tokyo, Japan (Mega-city/Islands)"),
        ("170", "055", "Cape Town, South Africa (Coastal/Mountain)"),
        
        # 🏜️ Deserts & Arid Landscapes
        ("233", "079", "Amazon Rainforest, Brazil (Dense Greenery)"),
        ("180", "040", "Sahara Desert Edge, Egypt (Sand/Rock)"),
        ("175", "043", "Nairobi, Kenya (Savanna/Urban)"),
        
        # 🌲 Forests, Agriculture, and Greenery
        ("192", "024", "Berlin, Germany (Temperate Forest/Urban)"),
        ("202", "024", "London, UK (Temperate/Agriculture)"),
        ("045", "029", "Yellowstone, USA (Forest/Geothermal)"),
        ("164", "043", "Mount Kilimanjaro, Tanzania (Snow/Mountain)"),
        ("113", "050", "Bali, Indonesia (Island/Volcano)"),
        
        # 🌊 Water Boundaries and Coastlines
        ("091", "086", "Great Barrier Reef Edge, Australia (Coast/Coral)"),
        ("022", "039", "Mississippi River Delta, USA (Wetlands)"),
        ("176", "039", "Dubai, UAE (Desert/Coast/Artificial Islands)"),
        ("001", "072", "Andes Mountains, Chile (Snow/Rock)"),
        ("117", "044", "Taipei, Taiwan (Tropical/Mountain)"),
        ("140", "041", "Kathmandu, Nepal (Himalayas)"),
        ("226", "071", "Rio de Janeiro, Brazil (Coastal/Forest)")
    ]
    
    # Slice the list to start from the START_INDEX
    # (Subtract 1 because lists are 0-indexed, but our regions start at 1)
    regions = regions[START_INDEX - 1:]
    
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
        
        # Check if download succeeded before running driver
        if os.path.exists(output_path) and os.listdir(output_path):
            # 2. Run driver.py
            driver_path = os.path.join(base_dir, 'driver.py')
            print("⚙️ Running driver.py to process patches...")
            try:
                subprocess.run(["python", driver_path], check=True)
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Warning: driver.py failed for {name}. Skipping to next region.")
        else:
            print(f"⚠️ Warning: Download failed or was empty for {name}. Skipping.")
        
        # 3. Clean up to save space!
        print("🧹 Cleaning up heavy raw files to save Kaggle disk space...")
        for folder in [input_dir, downscaled_dir, rgb_dir]:
            if os.path.exists(folder):
                shutil.rmtree(folder)
                
    print("\n✅ All regions processed! Your lightweight dataset is ready in output/patches/")

if __name__ == '__main__':
    run_massive_orchestrator()
