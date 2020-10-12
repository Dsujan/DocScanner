#importing os module
import os
import hashlib
import sqlite3
import time
import pprint

scan = None
infected_docs = []
os.system('cls')


option = input('\n\nEnter 1 to update signature and 2 for scanning\n\n')


if option == '1':

	scan = False

elif option == '2':

	scan = True

else:

	print('\nInvalid Input!')
	print('\nExiting program.....')
	time.sleep(1)
	quit()





#initialising databse
DB_NAME = 'SIGN_DB'
connectDb = sqlite3.connect(DB_NAME)
cursor = connectDb.cursor()


#creating new table for first time
try:

	cursor.execute('''CREATE TABLE signatures
         (ID INT PRIMARY KEY ,
         sig_value TEXT NOT NULL UNIQUE)
          ;''')

	print("\nSignature Table created successfully...");

	
except Exception as e:
	print('\nSignature Table already exists....')




print("\nStarting...\n")

#checking scanned signatures within exiting signature databse
def check_for_virus(check_against):
	all_signatures=[]
	#fetching signature database
	rows = cursor.execute('SELECT sig_value FROM signatures')
	for row in rows:
		#print(row)

		all_signatures.append(row)

	if check_against in [i[0] for i in all_signatures]: ##using list comprehension to convert a tuple list into element list
		return True;

	else:

		return False;



#updates the virus signature database
def update_signature(checksums):
	
	for checksum in checksums:
		try:
			cursor.execute("INSERT INTO signatures VALUES (NULL,?)",(checksum,))
			print('<<<1 New Signature Updated>>>')
		except:
			print('<<<Old Signature>>>')



#calculating checksum for each scanned files
def calc_checksum():
	checksum_list = []
	
	for doc in scanned_doc_files:
		with open(doc,encoding = "ISO-8859-1") as file_to_calc:
			file_data = file_to_calc.read().encode("ISO-8859-1")
			md5_checksum = hashlib.md5(file_data).hexdigest()
			checksum_list.append(md5_checksum)

			if scan:
				#checking scanned signature 
				if not check_for_virus(md5_checksum):
					infected_docs.append(doc)
					print('\nWarning!!!!!-----Threats found')

	#returns checksums to update in databse
	if not scan:
		return set(checksum_list)

#list of all possible drives.
#C drive took long time for scanning so its ommited for testing purpose
dr =  'ABDEFGHIJKLMNOPQRSTUVWXYZ'
#filtering live drives
drives = ['%s:' % d for d in dr if os.path.exists('%s:' % d)]

for drive in drives: 
	#stores scanned doc files
	print('\n\nScannig  ' + drive + '/ ...' )
	scanned_doc_files = []
	for subdir, dirs, files in os.walk(drive + os.sep):	
		for file  in files:
			scanned_file_path = subdir + os.sep + file
			if scanned_file_path.endswith(".doc") or scanned_file_path.endswith(".docx"):
				scanned_doc_files.append(scanned_file_path)


	#update db if only the program isn't started for scanning i.e for update
	if not scan:
		allcheck_sums =list(calc_checksum())
		update_signature(allcheck_sums)
	else:
		calc_checksum()

#showing threats
if infected_docs:
	pp = pprint.PrettyPrinter(indent=4)
	print('\n')
	pp.pprint(infected_docs)

#closing database conenctions
connectDb.commit()
connectDb.close()

if not scan:

	print('\n______________________________________________________________\n')
	print('_             SUCESSFULLY UPDATED                             _')
	print('______________________________________________________________\n')

else:
	print('\n______________________________________________________________\n')
	print('_              SCANNING COMPLETED                            _')
	print('               '+str(len(infected_docs))+' files infected      ')
	print('______________________________________________________________\n')
