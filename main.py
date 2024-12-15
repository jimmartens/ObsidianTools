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

def get_start_day_of_month(date_in_month=None):
    if date_in_month is None:
        date_in_month = datetime.now()
    else:
        date_in_month = datetime.strptime(date_in_month, '%Y-%m-%d')
    if start_day is "Sun": # TODO: Not sure if this is correct.
        mod = 1
    else:
        mod = 0
    start_day = date_in_month - timedelta(days=date_in_month.day + mod - 1)
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
        if file.endswith('.md') and not file.startswith('Summary_'):
            file_date = datetime.strptime(file.split('_')[0].split('.')[0], '%Y-%m-%d')
            if week_start_date <= file_date <= week_end_date:
                week_files.append(folder + file)
    week_files.sort()
    return week_files

def get_files_for_month(folder, month_start_date=None, start_day=None):
    month_start_date_str = get_start_day_of_week(month_start_date, start_day) # TODO: Change this to get the first day of the month
    month_start_date = datetime.strptime(month_start_date_str, '%Y-%m-%d')
    month_end_date = month_start_date + timedelta(days=30)
    print(f'start: {month_start_date} end {month_end_date}:')
    month_files = []
    for file in os.listdir(folder):
        if file.endswith('.md') and not file.startswith('Summary_'):
            file_date = datetime.strptime(file.split('_')[0].split('.')[0], '%Y-%m-%d')
            if month_start_date <= file_date <= month_end_date:
                month_files.append(folder + file)
    month_files.sort()

# Format of #tag or # header_name
# Should be able to summarize week/month/year.
def summary(folder, files, search_string, summary_type, start_date):
    
    folder = folder + '/' + summary_type
    if not os.path.exists(folder):
        os.mkdir(folder)
    summary_file = os.path.join(folder, f'{summary_type}Summary_{start_date}.md')
            
    if len(files) == 0:
        print(f'No files found for this {summary_type}.')
        return 0
        
    # Write a header to Summary File
    if os.path.exists(summary_file):
        os.remove(summary_file)
        f = open(summary_file, 'w')
        f.write(f'# Weekly Summary for {search_string} - {start_date}\n')
    else:
        f = open(summary_file, 'w')
        f.write(f'# Weekly Summary for {search_string} - {start_date}\n')
     
    # Iterate through files and add/remove tags/headers as necessary
    for file in files:
        with open(file, 'r') as f_read:
            content = f_read.read()
            if search_string in content:
                f.write(f'\n## search string \'{search_string}\' found in  {file}\n')
                f_read.seek(0)
                in_search_block = False

                while True:
                    line = f_read.readline()
                    if not line:
                        break
                    if in_search_block:
                        # check to see if this line starts with '##'  
                        if line.startswith('## '):
                            in_search_block = False
                        else:
                            f.write(line)
                    if search_string in line:
                        in_search_block = True
                        #f.write(line)

            else:
                f.write(f'\n## search string \'{search_string}\' not found in {file}\n')
    
    f.close()
    return 0

def list_files_for_current_and_sub_dirs():
    current_dir = os.getcwd()
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.md'):
                print(os.path.join(root, file))
    return 0    

# Read in Arguments
args = sys.argv
if len(args) > 1:
    folder = args[1]
else:
    folder = '.'

def main():
    print(f'Sunday of this week: {get_start_day_of_week(start_day="Sun")}')
    random_date = "2024-11-20" #should be 10/6 if Sun is selected
    print(f'Show entries for {random_date} ')
    print(f'Sunday for {random_date}: is {get_start_day_of_week(random_date, start_day="Sun")}')
    
    folder = 'test_files/jm/'

    weekly_files = get_files_for_week(folder, random_date, start_day="Sun")
    print(get_files_for_week(folder, random_date, start_day="Sun"))
    
    # Summary for week
    summary(folder, weekly_files, '## search string', 'weekly', get_start_day_of_week(random_date, start_day="Sun"))

    # Summary for month
    
    print('Done!')
    return 0

if __name__ == '__main__':
    main()