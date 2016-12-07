import shutil, json, time, sys, csv, os

# PROGRESS BAR STUFF
# Reference: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    if filled_len == bar_len:
    	bar = '=' * filled_len
    else:
    	bar = '=' * (filled_len - 1) + '>' + '-' * (bar_len - filled_len - 1)

    sys.stdout.write('[%s] %s%s ... %s\r' % (bar, percents, '%', status))
    sys.stdout.flush() # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)

# POLICE BEAT PROCESSOR
# User controlled variables
crime_file_name = "C:\\Users\\asoota\\Downloads\\Crimes_-_2001_to_present.csv"
beats_file_name = "C:\\Users\\asoota\\Downloads\\PoliceBeatDec2012.csv"
folder = "C:\\Users\\asoota\Desktop\ChicagoCrimeData-ByBeat\\"
skip_before_year = 2012  # This year is included

# Processor Code
# Get all the possible beat numbers
beat_nums = []
with open(beats_file_name, "r") as beats_file:
    progress(0, 10, "Collecting Chicago Police Beats Information")
    beats_file_parser = csv.reader(beats_file,
                                   delimiter=',',
				   quotechar='"',
                                   lineterminator='\n')
    beats_file_header = []
    # Iterate over the CSV
    for beat_line in beats_file_parser:
        if beats_file_header == []:
            beats_file_header.extend(beat_line)
            continue
        # Add the Beat Number
        beat_nums.append(beat_line[beats_file_header.index("BEAT_NUM")])

# Count the number of records
num_records = -1
with open(crime_file_name, "r") as crime_file:
	progress(0, 100, "Counting number of Chicago Crime Records since 2001...")
	num_records = len(crime_file.readlines()) - 1
	progress(100, 100, "Counting number of Chicago Crime Records since 2001...")
	print "\r"
	print "Number of records found: %d" % num_records
	progress(0, num_records, "Processing Chicago Crime Data since 2001... (%d of %d)" % (0, num_records))

# Remove and create the folder
shutil.rmtree(folder, ignore_errors=True)
os.makedirs(folder)

# Iterate over each record now
skipped_year_count, skipped_beat_count = 0, 0
file_data = {}
with open(crime_file_name, "r") as crime_file:
    crime_file_parser = csv.reader(crime_file,
                                   delimiter=',',
				   quotechar='"',
                                   lineterminator='\n')
    crime_file_header = []
    # Iterate over the CSV
    for idx, crime_row in enumerate(crime_file_parser):
        if crime_file_header == []:
            crime_file_header.extend(crime_row)
            continue
        # Check for the year
        if int(crime_row[crime_file_header.index("Date")][6:10]) <= skip_before_year:
            # Skip this year's record
            skipped_year_count = skipped_year_count + 1
            progress(idx + 1, num_records, "Processing Chicago Crime Data since 2001... (%d of %d)" % (idx + 1, num_records))
            continue
        # Else, find the primary type
        primary_type = crime_row[crime_file_header.index("Primary Type")]
        if primary_type not in file_data:
            file_data[primary_type] = {}
            file_data[primary_type]["__beatordering"] = beat_nums
        # Find the date
        date = crime_row[crime_file_header.index("Date")]
        date = date[:2] + "_" + date[6:10]
        if date not in file_data[primary_type]:
            file_data[primary_type][date] = [0 for _ in range(len(beat_nums))]
        # Now, find the beat number
        beat_number = crime_row[crime_file_header.index("Beat")]
        if beat_number not in beat_nums:
            # Skip this record but count it
            skipped_beat_count = skipped_beat_count + 1
            progress(idx + 1, num_records, "Processing Chicago Crime Data since 2001... (%d of %d)" % (idx + 1, num_records))
            continue
        # Else, increment
        file_data[primary_type][date][beat_nums.index(beat_number)] += 1
        # Update the progress
        progress(idx + 1, num_records, "Processing Chicago Crime Data since 2001... (%d of %d)" % (idx + 1, num_records))
    # Now, print some stats
    progress(num_records, num_records, "Processing Chicago Crime Data since 2001... (%d of %d)" % (num_records, num_records))
    print "\r"
    print "Skipped records due to year being out of bounds:", skipped_year_count
    print "Skipped records due to beats not being found in the pre-defined list:", skipped_beat_count
    print "\n"
    # Now, write to the file
    for idx, file_name in enumerate(file_data):
        with open(folder + file_name + '.json', "w") as write_file:
            progress(idx + 1, len(file_data), "Writing Chicago Crime Data by Police Beat since %d ... (%d of %d)" % (skip_before_year + 1, idx + 1, len(file_data)))
            json.dump(file_data[file_name], write_file)
    progress(1, 1, "Writing Chicago Crime Data by Police Beat since %d ... (%d of %d)" % (skip_before_year + 1, len(file_data), len(file_data)))
    print "\n"
    
