import os
import csv
import random
import shutil
from collections import defaultdict

# Set seed for reproducibility
random.seed(42)

csv_path = '/Users/rishika/Downloads/Image/Speed_dat_2W_2025.csv'
img_dir = '/Users/rishika/Downloads/Image/downloaded_images'
out_dir = '/Users/rishika/Downloads/Image/sampled_1080_dataset'
out_csv = '/Users/rishika/Downloads/Image/Ground_Truth_Annotation_1080.csv'

os.makedirs(out_dir, exist_ok=True)

print("Scanning downloaded images folder...")
downloaded_set = set(os.listdir(img_dir))
print(f"Total available images in downloaded_images: {len(downloaded_set):,}")

print("Reading Speed_dat_2W_2025.csv for Month 1 (January)...")
# Grid: (location, hour) -> list of candidate row dicts
grid = defaultdict(list)

with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, start=1):
        filename = f"{idx}.jpg"
        if filename in downloaded_set and row.get('month') == '1':
            loc = row.get('SystemCodeNumber')
            h_str = row.get('hour')
            if loc and h_str:
                h = int(h_str)
                row_info = {
                    'filename': filename,
                    'location': loc,
                    'year': row.get('year', '2025'),
                    'month': row.get('month', '1'),
                    'day': row.get('day'),
                    'hour': h,
                    'time': f"{h:02d}:{int(row.get('minute', 0)):02d}:{int(row.get('second', 0)):02d}",
                    'last_updated': row.get('LastUpdated', ''),
                    'speed': row.get('RecordedSpeed', ''),
                    'lane': row.get('Lane_Number', ''),
                    'violation': row.get('ViolationType', '')
                }
                grid[(loc, h)].append(row_info)

locations = sorted(list(set(loc for loc, h in grid.keys())))
hours = sorted(list(set(h for loc, h in grid.keys())))

print(f"\nFound {len(locations)} Locations: {locations}")
print(f"Found {len(hours)} Hours: {hours}")
print(f"Total (Location x Hour) combinations: {len(grid)}")

TARGET_PER_CELL = 10
sampled_records = []

for loc in locations:
    for h in hours:
        candidates = grid.get((loc, h), [])
        if not candidates:
            continue
        
        # Group candidates by day to ensure diversity across days of the month
        by_day = defaultdict(list)
        for c in candidates:
            by_day[c['day']].append(c)
        
        days = list(by_day.keys())
        random.shuffle(days)
        
        cell_selected = []
        # Round-robin selection across unique days
        day_idx = 0
        while len(cell_selected) < TARGET_PER_CELL and len(cell_selected) < len(candidates):
            d = days[day_idx % len(days)]
            if by_day[d]:
                pick = random.choice(by_day[d])
                by_day[d].remove(pick)
                cell_selected.append(pick)
            day_idx += 1
            if all(len(lst) == 0 for lst in by_day.values()):
                break
        
        sampled_records.extend(cell_selected)

print(f"\nTotal sampled records across all buckets: {len(sampled_records)}")

print("Copying sampled images into destination folder...")
copied_count = 0
for rec in sampled_records:
    src = os.path.join(img_dir, rec['filename'])
    dst = os.path.join(out_dir, rec['filename'])
    if os.path.exists(src) and not os.path.exists(dst):
        shutil.copy2(src, dst)
        copied_count += 1
    elif os.path.exists(dst):
        copied_count += 1

print(f"Successfully copied/verified {copied_count} images in {out_dir}")

# Write to Ground_Truth_Annotation_1080.csv
fieldnames = [
    'Image_File',
    'Location',
    'Date',
    'Time',
    'Hour',
    'Recorded_Speed',
    'Vehicle_Type',
    'Number_of_Riders',
    'Rider_Gender',
    'Rider_Helmet',
    'Pillion_Helmet',
    'Luggage',
    'Notes'
]

# Sort by Location and Hour for easy, organized annotation
sampled_records.sort(key=lambda x: (x['location'], x['hour'], int(x['day'])))

with open(out_csv, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for rec in sampled_records:
        writer.writerow({
            'Image_File': rec['filename'],
            'Location': rec['location'],
            'Date': f"2025-01-{int(rec['day']):02d}",
            'Time': rec['time'],
            'Hour': rec['hour'],
            'Recorded_Speed': rec['speed'],
            'Vehicle_Type': '',
            'Number_of_Riders': '',
            'Rider_Gender': '',
            'Rider_Helmet': '',
            'Pillion_Helmet': '',
            'Luggage': '',
            'Notes': ''
        })

print(f"Annotation sheet written to: {out_csv}")
print("Done!")
