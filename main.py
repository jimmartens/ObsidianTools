'''
A group of methods to:
- Add something to every note in a folder if it does not exist
- Remove something from every folder if it exists
- Weekly Summarization based on tag or header
- Replace a string in a file with another string

All files in folder are date based with the format YYYY-MM-DD.md
'''
import os
import sys
from datetime import datetime, timedelta

tags_to_add = [ '#fun', '#learning']
strings_to_remove = [ '{{title}}' ]
start_week = "Sun"

def modify_file(file):
    with open(file, 'r') as f:
        content = f.read()
    for tag in tags_to_add:
        if tag not in content:
            content += '\n' + tag
    for string in strings_to_remove:
        if string in content:
            content = content.replace(string, '')
    with open(file, 'w') as f:
        f.write(content)
    return 0

# Deprecated: does not really need to be used.
def move_files(files):
    for file in files:
        file_name = file.split('/')[-1]
        strings_to_remove.append(file_name)
        file_date = file_name.split('_')[0]
        print(f'Moving {file_name} to {file_date}')
        year = file_date.split('-')[0]
        month = file_date.split('-')[1]
        new_folder = f'./Month/{year}-{month}'
        if not os.path.exists(new_folder):
            os.makedirs(new_folder)
        os.rename(file, os.path.join(new_folder, file_name))

def get_start_day_of_week(date_in_week=None, start_day=None):
    if date_in_week is None:
        date_in_week = datetime.now()
    else:
        date_in_week = datetime.strptime(date_in_week, '%Y-%m-%d')
    if start_day is "Sun":
        mod = 1
    else:
        mod = 0
    start_day = date_in_week - timedelta(days=date_in_week.weekday() + mod)
    return start_day.strftime('%Y-%m-%d')

# Iterate through a list of files and build a list of unique Headers based on the number of #s in the header.
def get_unique_headers(files):
    headers = set()
    for file in files:
        with open(file, 'r') as f:
            content = f.read()
        header_count = content.count('#')
        if header_count > 0:
            header = content.split('\n')[0]
            headers.add(header)
    return list(headers)

# Given a string return all content that matches that block of text.
def get_content_by_block(file, block_text):
    with open(file, 'r') as f:
        content = f.read()
    start_index = content.find(block_text)
    if start_index!= -1:
        end_index = content.find('\n', start_index)
        if end_index!= -1:
            return content[start_index:end_index]
    return ''

# Given a list of files with the format YYYY-MM-DD.md return a list of files that make up one week's worth of files starting from week_start_date.
def get_files_for_week(folder, week_start_date=None, start_day=None):
    week_start_date_str = get_start_day_of_week(week_start_date, start_day)
    week_start_date = datetime.strptime(week_start_date_str, '%Y-%m-%d')
    week_end_date = week_start_date + timedelta(days=6)
    print(f'start: {week_start_date} end {week_end_date}:')
    week_files = []
    for file in os.listdir(folder):
        if file.endswith('.md') and not file.startswith('Summary_'): # TODO: this should go away as the file should be written to a weekly folder.
            print(f'file: {file}')
            file_date = datetime.strptime(file.split('_')[0].split('.')[0], '%Y-%m-%d')
            if week_start_date <= file_date <= week_end_date:
                week_files.append(file)
    return week_files #[file for file in os.listdir(folder) if week_start_date <= datetime.strptime(file.split('_')[0].split('.')[0], '%Y-%m-%d') <= week_end_date]

# Problem here is that I would then have to iterate through the directory again, because I am only storying the file name. 
# I could instead call them from here.  
# Can I sort the files first?


# Summarize weekly collection of tags or headers.  
# Format of #tag or # header_name
def weekly_summary(folder, search_string, week_files=None, day_in_week=None, start_day=None):
    # Create or overwrite a Summary File for the week 
    week_start_date = get_start_day_of_week(day_in_week, start_day) # Seems redundant.
    
    summary_file = os.path.join(folder, f'Summary_{get_start_day_of_week(week_start_date, start_day)}.md')
    
    # Write a header to Summary File
    if os.path.exists(summary_file):
        os.remove(summary_file)
        with open(summary_file, 'w') as f:
            f.write(f'# Weekly Summary for {search_string} - {get_start_day_of_week(week_start_date, start_day)}\n')
    else:
        with open(summary_file, 'w') as f:
            f.write(f'# Weekly Summary for {search_string} - {get_start_day_of_week(week_start_date, start_day)}\n')
    
    ''' 
    # Iterate through files and add/remove tags/headers as necessary
    for file in week_files:
        if search_string in file:
            print(f'Weekly Summary for {search_string} in {file}:')
            modify_file(os.path.join(folder, file))
            # weekly_summary_helper(os.path.join(folder, file), search_string)
        else:
            print('No tag or header found.')
    '''
    f.close()
    return 0

def list_files_for_current_and_sub_dirs():
    current_dir = os.getcwd()
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.md'):
                print(os.path.join(root, file))
    return 0    

def read_files_current_dir():
    files = os.listdir()
    mdfiles = []
    for file in files:
        if file.endswith('.md'):
            mdfiles.append(file)
    return mdfiles

# Read in Arguments
args = sys.argv
if len(args) > 1:
    folder = args[1]
else:
    folder = '.'

def main():
    # files = read_files_current_dir()
    # print(f'Moving {len(files)} files...')
    # list_files_for_current_and_sub_dirs()
    print(f'Sunday of this week: {get_start_day_of_week(start_day="Sun")}')
    randomDate = "2024-11-20" #should be 10/6 if Sun is selected
    print(f'Show entries for {randomDate} ')
    print(f'Sunday for {randomDate}: is {get_start_day_of_week(randomDate, start_day="Sun")}')
    
    print(get_files_for_week('.', randomDate, start_day="Sun"))
    
    weekly_summary('.', '#fun')
    
    print('Done!')
    return 0

if __name__ == '__main__':
    main()