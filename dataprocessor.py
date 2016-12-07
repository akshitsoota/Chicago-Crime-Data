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
    	bar = '=' * (filled_len - 1) + '>' + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ... %s\r' % (bar, percents, '%', status))
    sys.stdout.flush() # As suggested by Rom Ruben (see: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console/27871113#comment50529068_27871113)

# CRIME DATA PROCESSOR
# User controlled variables
file_name = "/home/axe/Downloads/Crimes_-_2001_to_present.csv"

# Processor code
extract = {"desc_month_year": [['Primary Type', []],
			       ['Date', [(0, 2), (6, 10)]]]}
flex = {"_condensed": ["ID", "Date", "Primary Type", "Beat"]}
conditions = {}
debug_break_point_processing = None
debug_run_count_check_on_folders = True 

# Some pre-processing
if len(extract) == 0:
	print "Must have some information to extract"
	sys.exit(0)
if len(flex) == 0:
	flex = {"": []}
if len(conditions) == 0:
	conditions = {"_": lambda _, __: True}

# Count the number of records
num_records = -1
with open(file_name, "r") as crime_file:
	progress(0, 100, "Counting number of Chicago Crime Records since 2001...")
	num_records = len(crime_file.readlines()) - 1
	progress(100, 100, "Counting number of Chicago Crime Records since 2001...")
	print "\r"
	print "Number of records found: %d" % num_records
	progress(0, num_records, "Processing Chicago Crime Data since 2001... (%d of %d)" % 
				 (0, (num_records * (len(extract) * len(flex) * len(conditions)))))

# Clean up the directories and initialize them too
for folder_name in extract:
	shutil.rmtree(folder_name, ignore_errors=True)
	os.makedirs(folder_name)

# Now, go over each record
progress_count, total_count = 0, num_records * len(extract) * len(flex) * len(conditions)
files_created = {}
# Open each file based on extract and flex
for class_name, classification_criteria in extract.iteritems():
	for file_extension, required_fields in flex.iteritems():
		with open(file_name, "r") as crime_file:
			# Open the CSV and start processing each row
			crime_csv_parser = csv.reader(crime_file,
					      	delimiter=',',
					      	quotechar='"',
					      	lineterminator='\n')
			header = []
			for counter, row in enumerate(crime_csv_parser):
				# Catch header if we haven't got it
				if header == []:
					header.extend(row)
					continue
				# Check that this row meets all the conditions
				meet_all_conditions = True
				for _, condition_func in conditions.iteritems():
					meet_all_conditions = meet_all_conditions and condition_func(class_name, row)
				if not meet_all_conditions:
					# Skip this iteration but update the progress
					progress_count = progress_count + 1
					progress(progress_count, total_count, "Processing Chicago Crime Data since 2001... (%d of %d)" % (progress_count, total_count))
				# For each criteria, form the file name
				dest_file_name = []
				for criteria_item in classification_criteria:
					column_name, split_points = criteria_item
					# Start extracting the information
					field_item = row[header.index(column_name)]
					new_field = field_item
					if len(split_points) != 0:
						new_field = "_".join([field_item[start:end] for start, end in split_points])
					new_field = new_field.replace("/", "_").replace(" ", "_")
					# Add to the dest_file_name
					dest_file_name.append(new_field)
				# Make the row into a dictionary
				neat_row = {}
				if required_fields == []:
					# Get them all
					neat_row = {header[idx]: row[idx] for idx in range(len(header))}
				else:
					# Filter
					neat_row = {header[idx]: row[idx] for idx in range(len(header)) if header[idx] in required_fields}
				# Form the file name and check in hashmap and add as necessary
				dest_file_name = "_".join(dest_file_name)
				dest_file_name = os.path.join(class_name, dest_file_name + file_extension + '.json')
				if dest_file_name in files_created:
					with open(dest_file_name, "a") as write_to:
						write_to.write(",%s" % (json.dumps(neat_row)))
				else:
					with open(dest_file_name, "w") as write_to:
						write_to.write("[%s" % (json.dumps(neat_row)))
					files_created[dest_file_name] = True
				# Print progress
				progress_count = progress_count + 1
				progress(progress_count, total_count, "Processing Chicago Crime Data since 2001... (%d of %d)" % (progress_count, total_count))
				# Check for break point
				if debug_break_point_processing is not None and \
			   	   counter >= debug_break_point_processing: break
# Close the list parenthesis for each of the files
for file_name in files_created:
	with open(file_name, "a") as write_to:
		write_to.write("]")
# Run checks if enabled
if debug_run_count_check_on_folders == True:
	print "\r"
	# Check if assertion can be done because of the conditions
	if len(conditions) > 1 or "_" not in conditions:
		print "Unable to assert count because of conditions being placed on the output objects"
		sys.exit(-1)
	# Assertion can be done
	progress(0, len(files_created), "Asserting folder and file object sum integrity (0 of %d)" % len(files_created))
	progress_count = 0
	# Classify
	folder_file_mapping = {}
	for file_name in files_created:
		folder, file_name = file_name.split("/")
		if folder in folder_file_mapping:
			folder_file_mapping[folder].append(file_name)
		else:
			folder_file_mapping[folder] = [file_name]
	# Now, sum and check
	folder_count_mapping = {folder: 0 for folder in folder_file_mapping}
	for folder_name, file_names in folder_file_mapping.iteritems():
		for file_name in file_names:
			with open(os.path.join(folder_name, file_name), "r") as file_to_count_in:
				folder_count_mapping[folder_name] += len(json.load(file_to_count_in))
			# Increment progress
			progress_count = progress_count + 1
			progress(progress_count, len(files_created), "Asserting folder and file object sum integrity (%d of %d)" % (progress_count, len(files_created)))
		# Run assert
		try:
			assert folder_count_mapping[folder_name] == num_records
		except AssertionError:
			print "\r\nAssertion failed on folder %s with files" % folder_name
			print file_names
			sys.exit(-1)

# Print and exit
print "\r"
