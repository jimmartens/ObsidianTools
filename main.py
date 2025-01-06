'''
A group of methods to:
- Add something to every note in a folder if it does not exist
- Remove something from every folder if it exists
- Weekly Summarization based on tag or header
- Replace a string in a file with another string

All files in folder are date based with the format YYYY-MM-DD.md
'''
import os
from datetime import datetime, timedelta
import argparse

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
    if start_day == "Sun":
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
    if start_day == "Sun": # TODO: Not sure if this is correct.
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

''' NOTES:
- Change File Name to YYYY-MM-DD_summary_searchstring.md - Remove any # from the file name
'''
# Format of #tag or # header_name
# Should be able to summarize week/month/year.
def summary(folder, files, search_string, summary_type, start_date):
    
    # Set end string to leading #^n from the search string
    index = search_string.find('# ')
    end_string = search_string[:index+2]
    
    folder = folder + '/' + summary_type
    if not os.path.exists(folder):
        os.mkdir(folder)
    summary_file = os.path.join(folder, f'{start_date}_summary_{search_string}.md')
            
    if len(files) == 0:
        print(f'No files found for this {summary_type}.')
        return 0
        
    # Write a header to Summary File
    if os.path.exists(summary_file):
        answer = input(f'Summary file already exists. Do you want to overwrite it? (y/n): ')
        if answer.lower()!= 'y':
            return 0
        os.remove(summary_file)
        f = open(summary_file, 'w')
        f.write(f'# Weekly Summary for \'{search_string}\' - {start_date}\n')
    else:
        f = open(summary_file, 'w')
        f.write(f'# Weekly Summary for \'{search_string}\' - {start_date}\n')
     
    # Iterate through files and add/remove tags/headers as necessary
    for file in files:
        with open(file, 'r') as f_read:
            content = f_read.read()
            if search_string in content:
                f.write(f'## Results from: {file}\n')
                f_read.seek(0)
                in_search_block = False

                while True:
                    line = f_read.readline()
                    if not line:
                        break
                    if in_search_block:
                        # check to see if this line starts with '##'  
                        if line.startswith(end_string):
                            in_search_block = False
                        else:
                            f.write(line)
                    if search_string in line:
                        in_search_block = True
    f.close()
    return 0

#Change it to having a start directory as input, 
def list_files_for_current_and_sub_dirs(folder='.'):
    current_dir = os.getcwd()
    for root, dirs, files in os.walk(current_dir):
        for file in files:
            if file.endswith('.md'):
                print(os.path.join(root, file))
    # Should return a list of all files in the current directory and its subdirectories.
    return 0    

# Add a tag or tags to all files in a directory and its subdirectories
def add_tag_to_files(folder, tags, start_day=None):
    return None

def setup_parser():
    parser = argparse.ArgumentParser(description="Parsing the arguments")
    parser.add_argument(
        '--folder', 
        type=str, 
        required=False, 
        default='.', 
        help='Path to the folder to process (default: current directory)')
    parser.add_argument(
        '--mode',
        choices=['replace', 'sum', 'remove'],
        default='sum',
        help='Processing mode to use (default: fast)'
    )
    parser.add_argument(
        '--range',
        type=str,
        choices=['week','month', 'quarter', 'year'], 
        default='week',
        help='Date range to process.'
    )
    parser.add_argument('--start_day', type=str, choices=['Sun', 'Mon'], default='Sun', help='Start day of the week for range (default: Sun)')
    parser.add_argument('--date', type=str, help='Date to process (if not provided, defaults to current date) format: YYYY-MM-DD')
    parser.add_argument('--tag', type=str, help='Tag to filter notes for weekly summary')
    parser.add_argument('--header', type=str, help='Header to filter notes for weekly summary')
    parser.add_argument('--search_string', type=str, help='String to search for in files format: #tag or # header_name')
    return parser

def main():
    parser = setup_parser()
    args = parser.parse_args()
    
    if args.mode =='replace':
        # Replace files with new content
        print('Mode not implemented yet')
        pass
    elif args.mode =='sum':
        # Summarize files based on search string

        if args.date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        else:
            target_date = args.date
        
        print(f'Show entries for {target_date} ')
        print(f'Sunday for {target_date}: is {get_start_day_of_week(target_date, start_day=args.start_day)}')
    
        if args.folder is None:
            folder = '.'
        else:
            folder = args.folder

        if args.search_string is None:
            print('Search string is required')
            return 1
        else: 
            search_string = args.search_string
            
        weekly_files = get_files_for_week(folder, target_date, start_day=args.start_day)
        print(get_files_for_week(folder, target_date, start_day=args.start_day))
           
        print(f'Searching for: {args.search_string}')
        summary(folder, weekly_files, search_string, args.range, get_start_day_of_week(target_date, start_day=args.start_day))
        #summary(args.folder, list_files_for_current_and_sub_dirs(args.folder), args.search_string, args.range, args.date)
    elif args.mode =='remove':
        # Remove tags/headers from files
        print('Mode not implemented yet')
        pass
    else:
        print('Invalid mode')
        return 1
         
    # for test purposes, running the script with some arguments.
    # python main.py --mode sum --range week --date 2024-11-20 --search_string '## search string' --folder test_files/jm/
    # Problem here is the space. 
    # TODO: Get pretty print or something similar to clear on save.  There are some whitespaces in the output currently.

    return 0

if __name__ == '__main__':
    main()