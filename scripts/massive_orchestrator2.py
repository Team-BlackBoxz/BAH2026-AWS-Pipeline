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
        # Extreme Cold & Ice
        ("069", "017", "Anchorage, USA (Snow/Ice)"),
        ("196", "018", "Oslo, Norway (Snow/Forest)"),
        ("186", "018", "Helsinki, Finland (Snow/Forest)"),
        ("218", "015", "Reykjavik, Iceland (Volcano/Ice)"),
        ("011", "014", "Nuuk, Greenland (Ice/Rock)"),
        
        # Dense Global Hubs
        ("044", "034", "San Francisco, USA (Coastal/Urban)"),
        ("023", "031", "Chicago, USA (Lake/Urban)"),
        ("219", "076", "Sao Paulo, Brazil (Dense Urban)"),
        ("110", "035", "Kyoto, Japan (Urban/Forest)"),
        ("198", "024", "Amsterdam, Netherlands (Coastal/Urban)"),
        
        # Deserts & Arid
        ("176", "039", "Cairo, Egypt (Desert/Urban)"),
        ("169", "037", "Baghdad, Iraq (Desert/Urban)"),
        ("037", "037", "Phoenix, USA (Desert)"),
        ("202", "037", "Casablanca, Morocco (Coastal/Arid)"),
        ("205", "050", "Dakar, Senegal (Coastal/Tropical)"),
        
        # Tropical Islands & Coastlines
        ("074", "072", "Suva, Fiji (Tropical/Island)"),
        ("158", "073", "Antananarivo, Madagascar (Island/Tropical)"),
        ("072", "086", "Auckland, New Zealand (Coastal/Island)"),
        ("015", "042", "Miami, USA (Tropical/Coastal)"),
        
        # Rivers & Mountains
        ("004", "053", "Caracas, Venezuela (Mountain/Urban)"),
        ("168", "054", "Addis Ababa, Ethiopia (Mountain/Urban)"),
        ("138", "044", "Kolkata, India (River/Urban)"),
        ("137", "043", "Dhaka, Bangladesh (River/Tropical)"),
        ("193", "027", "Munich, Germany (Forest/Urban)"),
        ("190", "027", "Vienna, Austria (Urban)")
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
