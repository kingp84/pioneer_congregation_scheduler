# Congregation Scheduler

This app generates monthly assignment schedules for the Pioneer Church of Christ.

## Features
- Reads directory from `data/Pioneer Directory.csv`
- Applies fixed rules (Steve → Lord's Supper, Earl → Teaching, Preaching rotation)
- Rotates communion prep/cleanup and building cleanup
- Outputs schedules tied to real calendar dates

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt