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
        # Deserts
        ("039", "035", "Las Vegas, USA (Desert)"),
        ("006", "071", "Lima, Peru (Desert/Coastal)"),
        ("165", "043", "Riyadh, Saudi Arabia (Desert)"),
        ("176", "043", "Tehran, Iran (Desert/Mountains)"),
        
        # Snow & Mountains
        ("047", "026", "Vancouver, Canada (Snow/Forest)"),
        ("178", "021", "Moscow, Russia (Snow/Urban)"),
        ("034", "032", "Denver, USA (Mountains/Urban)"),
        ("007", "057", "Bogota, Colombia (Mountains)"),
        
        # Dense Urban Metropolises
        ("199", "024", "Paris, France (Urban)"),
        ("191", "031", "Rome, Italy (Urban/Historical)"),
        ("123", "032", "Beijing, China (Dense Urban)"),
        ("116", "034", "Seoul, South Korea (Mountains/Urban)"),
        ("181", "031", "Istanbul, Turkey (Urban/Coastal)"),
        ("195", "028", "Madrid, Spain (Urban)"),
        
        # Tropical & Coastal
        ("089", "084", "Sydney, Australia (Coastal/Urban)"),
        ("130", "054", "Bangkok, Thailand (Tropical Urban)"),
        ("189", "055", "Lagos, Nigeria (Coastal/Tropical)"),
        ("066", "045", "Honolulu, Hawaii (Volcano/Island)"),
        ("023", "039", "Houston, USA (Coastal Urban)"),
        ("225", "084", "Buenos Aires, Argentina (Coastal)"),
        
        # Diverse Additions
        ("170", "078", "Johannesburg, South Africa (Urban/Arid)"),
        ("183", "033", "Athens, Greece (Coastal/Historical)"),
        ("026", "047", "Mexico City, Mexico (High Altitude Urban)"),
        ("015", "033", "Washington DC, USA (Urban/Forest)"),
        ("200", "024", "Brussels, Belgium (Urban/Agriculture)")
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
