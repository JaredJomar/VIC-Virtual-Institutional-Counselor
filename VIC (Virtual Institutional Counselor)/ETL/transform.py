import os
import requests
import pandas as pd
from pathlib import Path
import concurrent.futures
from tqdm import tqdm
from datetime import time, timedelta, datetime

class Transform:
    def __init__(self, courses_df, meetings_df, requisites_df, rooms_df, sections_df, syllabus_dir="syllabuses/"):
        self.courses_df = courses_df
        self.meetings_df = meetings_df
        self.requisites_df = requisites_df
        self.sections_df = sections_df
        self.rooms_df = rooms_df
        self.syllabus_dir = syllabus_dir  # Specify the directory for syllabuses

    def clean_courses(self):
        """Ensure course IDs start from 2 and include the dummy record (cid=37)."""
        self.courses_df['classid'] = self.courses_df['classid'].astype(int)
        self.courses_df = self.courses_df[(self.courses_df['classid'] >= 2) | (self.courses_df['classid'] == 37)].reset_index(drop=True)

    def clean_requisites(self):
        """Remove references to the dummy course (cid=37) in requisites."""
        self.requisites_df = self.requisites_df[
            (self.requisites_df['cid'] != 37) & (self.requisites_df['requisiteid'] != 37)
        ].reset_index(drop=True)

    def resolve_section_conflicts(self):
        """Resolve conflicts where sections overlap in the same room or the same course, and exclude sections with classid 37."""
        schedules_df = self.sections_df.merge(self.meetings_df, left_on='meeting_id', right_on='mid')
        schedules_df['start'] = pd.to_datetime(schedules_df['start'], format='%H:%M:%S').dt.time
        schedules_df['end'] = pd.to_datetime(schedules_df['end'], format='%H:%M:%S').dt.time
        schedules_df = schedules_df[schedules_df['class_id'] != 37]

        sids_to_drop = set()
        for (room_id, day), group in schedules_df.groupby(['room_id', 'day']):
            sorted_group = group.sort_values(by=['start', 'end'])
            for i, row1 in sorted_group.iterrows():
                for j, row2 in sorted_group.iterrows():
                    if i >= j:
                        continue
                    if (row1['start'] < row2['end']) and (row2['start'] < row1['end']) and \
                    (row1['year'] == row2['year']) and (row1['semester'] == row2['semester']):
                        sids_to_drop.add(max(row1['sid'], row2['sid']))

        self.sections_df = self.sections_df[~self.sections_df['sid'].isin(sids_to_drop)].reset_index(drop=True)

    def filter_meetings(self):
        """Filter out invalid meetings and adjust those that go beyond valid time ranges."""
        self.meetings_df['time_start'] = pd.to_datetime(self.meetings_df['start']).dt.time
        self.meetings_df['time_end'] = pd.to_datetime(self.meetings_df['end']).dt.time

        morning_start = time(7, 30)
        morning_end = time(10, 15)
        afternoon_start = time(12, 30)
        afternoon_end = time(19, 45)

        invalid_meetings = self.meetings_df[
            (self.meetings_df['day'] == 'MJ') & (
                (self.meetings_df['time_start'] < morning_start) | 
                (self.meetings_df['time_end'] > morning_end) | 
                (self.meetings_df['time_start'] < afternoon_start) | 
                (self.meetings_df['time_end'] > afternoon_end)
            )
        ]
        self.meetings_df.drop(invalid_meetings.index, inplace=True)

    def validate_meeting_durations(self):
        """Ensure 'LMV' meetings are 50 minutes and 'MJ' meetings are 75 minutes."""
        self.meetings_df['minute_start'] = pd.to_datetime(self.meetings_df['start'], format='%H:%M:%S')
        self.meetings_df['minute_end'] = pd.to_datetime(self.meetings_df['end'], format='%H:%M:%S')
        self.meetings_df['duration'] = (self.meetings_df['minute_end'] - self.meetings_df['minute_start']).dt.total_seconds() / 60

        expected_duration = {'LMV': 50.0, 'MJ': 75.0}
        invalid_durations = self.meetings_df[
            self.meetings_df.apply(lambda row: expected_duration.get(row['day'], row['duration']) != row['duration'], axis=1)
        ]
        self.meetings_df.drop(invalid_durations.index, inplace=True)

    def check_overcapacity(self):
        """Ensure sections do not exceed room capacity."""
        sections_availability = self.sections_df.merge(self.rooms_df, left_on='room_id', right_on='rid', how='left')
        overcapacity_sections = sections_availability[sections_availability['capacity_x'] > sections_availability['capacity_y']]
        sids_to_drop = overcapacity_sections['sid'].tolist()
        self.sections_df = self.sections_df[~self.sections_df['sid'].isin(sids_to_drop)].reset_index(drop=True)

    def validate_sections(self):
        """Validate sections based on class, meeting, and room data, excluding references to dummy class."""
        valid_enrollment_df = self.sections_df[self.sections_df['class_id'] != 37]
        valid_meeting_ids = self.meetings_df['mid'].unique()
        valid_enrollment_df = valid_enrollment_df[valid_enrollment_df['meeting_id'].isin(valid_meeting_ids)]
        valid_enrollment_df = valid_enrollment_df.merge(self.courses_df, left_on="class_id", right_on="classid")
        valid_enrollment_df = valid_enrollment_df.merge(self.rooms_df, left_on="room_id", right_on="rid")
        valid_sids = valid_enrollment_df['sid'].values
        self.sections_df = self.sections_df[self.sections_df['sid'].isin(valid_sids)].reset_index(drop=True)

    def adjust_timestamps(self):
        """Adjust timestamps for meetings based on the year and semester."""
        meetings_with_year = self.meetings_df.merge(self.sections_df[['meeting_id', 'year', 'semester']], left_on='mid', right_on='meeting_id', how='left')
        semester_dates = {'Fall': (9, 1), 'Spring': (1, 15), 'V2': (6, 1)}
        meetings_with_year['month'] = meetings_with_year['semester'].map(lambda x: semester_dates.get(x, (1, 1))[0])
        meetings_with_year['day'] = meetings_with_year['semester'].map(lambda x: semester_dates.get(x, (1, 1))[1])
        meetings_with_year['start_datetime'] = meetings_with_year.apply(
            lambda row: datetime(year=row['year'], month=row['month'], day=row['day'],
                                 hour=int(row['start'].split(':')[0]),
                                 minute=int(row['start'].split(':')[1])), axis=1)
        meetings_with_year['end_datetime'] = meetings_with_year.apply(
            lambda row: datetime(year=row['year'], month=row['month'], day=row['day'],
                                 hour=int(row['end'].split(':')[0]),
                                 minute=int(row['end'].split(':')[1])), axis=1)
        self.meetings_df['start'] = meetings_with_year['start_datetime']
        self.meetings_df['end'] = meetings_with_year['end_datetime']

    def download_syllabus(self, course_info):
        """Download a single syllabus file."""
        try:
            # Get course information safely
            code = course_info['classes'].get('code', 'UNKNOWN')
            name = course_info['classes'].get('name', 'UNKNOWN')
            description = course_info.get('description', 'NoDescription').strip()
            syllabus_url = course_info.get('syllabus', '').strip()

            if not syllabus_url or syllabus_url.lower() == 'none':
                print(f"[ETL] No valid URL for {code}, skipping download.")
                return None

            # Construct the filename using the format
            filename = f'{name}-{code}-{description}.pdf'.replace(' ', '-').replace('/', '_')
            filepath = Path(self.syllabus_dir) / filename  # Use the dynamic syllabus_dir

            # Skip if file already exists
            if filepath.exists():
                print(f"[ETL] Syllabus already exists: {filename}")
                return filepath

            # Create directory if it doesn't exist
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Download the syllabus file
            response = requests.get(syllabus_url)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"[ETL] Downloaded: {filename}")
            return filepath

        except requests.exceptions.RequestException as e:
            print(f"[ETL] Failed to download {syllabus_url}: {str(e)}")
            return None
        except Exception as e:
            print(f"[ETL] Error processing {course_info['classes'].get('code', 'UNKNOWN')}: {str(e)}")
            return None

    def parallel_download_syllabi(self):
        """Download all syllabi in parallel."""
        print("[ETL] Starting parallel syllabus downloads...")

        # Create progress bar
        pbar = tqdm(total=len(self.courses_df), desc="[ETL] Downloading syllabi")

        # Use ThreadPoolExecutor for parallel downloads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all download tasks
            future_to_course = {
                executor.submit(self.download_syllabus, row): row 
                for _, row in self.courses_df.iterrows()
            }

            # Process completed downloads
            downloaded_files = []
            for future in concurrent.futures.as_completed(future_to_course):
                course = future_to_course[future]
                try:
                    filepath = future.result()
                    if filepath:
                        downloaded_files.append({
                            'code': course['classes'].get('code', 'UNKNOWN'),
                            'filepath': filepath
                        })
                except Exception as e:
                    print(f"[ETL] Download failed for {course['classes'].get('code', 'UNKNOWN')}: {str(e)}")
                finally:
                    pbar.update(1)

        pbar.close()
        # print(f"Downloaded {len(downloaded_files)} syllabi successfully")
        return downloaded_files

    def transform_all(self):
        """Execute all transformations on the data."""
        self.clean_courses()
        self.clean_requisites()
        self.resolve_section_conflicts()
        self.filter_meetings()
        self.validate_meeting_durations()
        self.check_overcapacity()
        self.validate_sections()
        self.adjust_timestamps()
        self.parallel_download_syllabi()

        print("[ETL] Transformations complete.")
        
        return self.courses_df, self.meetings_df, self.requisites_df, self.rooms_df, self.sections_df
