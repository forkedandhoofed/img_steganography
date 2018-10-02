#============================================================================================================================
#			A BRIEF (OR MAYBE NOT) SUMMARY OF MY ENCODING/DECODING TECHNIQUE
#I am using the first pixel to determine the location of the pixels I have altered to store the secret message
#I also use an interval of 15 to hide messages, i.e. secret pixels are always 15 pixels apart.
#Let R, G, B be the red, green, blue values of the first pixel of the image,
#(R*G*B) % 15 will the location coefficient of the secret pixels
#for example,
#if (R*G*B) % 15 = 0, the altered pixels will be the 2nd, 17th, 32nd, 47th, 62th, etc (since the first pixel is reserved for special use)
#if (R*G*B) % 15 = 5, the altered pixels will be the 7th, 22nd, 37th, 52nd, 67th, etc
#etc etc etc etc
#Making use of the fact that the ASCII character ord() codes only goes up to a maximum of 256
#hence, 15 pixels after the last pixel we have tampered with, we insert value above 257 to the last digit of its R, G, B values
#a random number generator is used here to ensure that the "STOP" sign pixel does not always give 257, but 257 plus a random integer
#for enhanced security.
#When decoding, this serves as a message to the algorithm that we have arrived at the end of the secret message.
#=============================================================================================================================

from easygui import *
from os import listdir
from png import *
from math import *
from easygui import *
from random import *

def get_image(f):
	#a function that converts a .png file into a list of lists
	print "starting to read",f
	r = Reader(filename=f)
	image = list(r.read()[2])
	print "finished reading", f
	new_image = []
	for row in image:
		new_row = row.tolist()
		new_image.append(new_row)
	return new_image

def choose_png(msg):
	# select a PNG image file and call get_image to load it
	filenames = listdir('.')
	fn2 = filenames[:]
	for f in fn2:
		if f[-3:] != 'png':
			filenames.remove(f)
	f = choicebox(msg,"",filenames)
	return get_image(f)

def get_txt(f):
	#converts a .txt file into a list of ASCII codes
	txt = open(f, 'r').read()
	txt_list = []
	for i in txt:
		txt_list.append(ord(i))
	return txt_list

def choose_txt(msg):
	#you choose a .txt file and call get_txt to load it
	filenames = listdir('.')
	fn3 = filenames[:]
	for f in fn3:
		if f[-3:] != 'txt':
			filenames.remove(f)
	f = choicebox(msg,"",filenames)
	return get_txt(f)

def save_image(image):
	# save the current image to a file
	if len(image) == 0:
		msgbox("No image to save")
		exit()
	name = enterbox("Please enter the file name for the saved image")
	if name[-4:] != '.png':
		name = name + '.png'
	from_array(image,"RGB").save(name)  
	return image

def save_text(text):
	#saves a string into a .txt file
	name = enterbox("Please enter the file name for the saved text")
	if name[-4:] != '.txt':
		name = name + '.txt'
	fout = open(name,"w")
	fout.write(text)
	fout.close()


def select_num(val,a,b):
	#deals with a situation in the process of encoding, when you have two numbers that ends with the digit we want
	#but we want to find the closest value, and make sure that value doesn't go above 255 or below 0
	if (abs(a-val) < abs(b-val)):
		if a < 0:
			return b
		else:
			return a
	else:
		if b > 255:
			return a
		else:
			return b

def change_num(list,p,new_num):
	#a function that takes the list, the position coefficient, and the new number that's supposed to be "inserted" into the image(list)
	#probably makes more sense if you read the main programme and come back to this afterwards
	a = (list[p]/10-1)*10 + (new_num/100)
	b = (list[p]/10+1)*10 + (new_num/100)
	list[p] = select_num(list[p],a,b)
	c = (list[p+1]/10-1)*10 + (new_num/10 - new_num/100*10)
	d = (list[p+1]/10+1)*10 + (new_num/10 - new_num/100*10)
	list[p+1] = select_num(list[p+1],c,d)
	e = (list[p+2]/10-1)*10 + (new_num - new_num/10*10)
	f = (list[p+2]/10+1)*10 + (new_num - new_num/10*10)
	list[p+2] = select_num(list[p+2],e,f)

def hide_message():
	image = choose_png("Select the original image where you want to hide the secret message. ")
	#a list of lists. image is the png file.
	row = len(image)
	col = len(image[0])
	flat_list_image = []
	for i in range(len(image)):
		flat_list_image.extend(image[i])
	msg_to_encode = choose_txt("Select the .txt file that contains your secret message.")
	if (row*col/3) < (15*(len(msg_to_encode)-1)+1):
		#length check. if the total number of pixels is less than [15*(msg length-1)+1], the message is too long for the image
		#we always reserve the very first pixel for the remainder that determines the position of secret pixels
		#and we reserve the last 15 pixels to put a "STOP" sign for decoding, i mean, we put a number greater than or equal to 257
		msgbox("It is not possible to encode this message into the image you selected due to the size of the image.")
		exit()
	p = (image[0][0]*image[0][1]*image[0][2]) % 15		#position coefficient
	for j in range(len(msg_to_encode)): 
		#the j-th code in encoded_msg will go to the (p+15j+1)-th pixel of the image
		change_num(flat_list_image,3*(p+15*j+1),msg_to_encode[j])
	change_num(flat_list_image,3*(p+15*len(msg_to_encode)+1),257+randint(0,500))	# we put a number (257+randint(0,500)) 15 pixels after the last secret pixel, serves as a "STOP" sign.
	encoded_image = []
	for k in range(row):
		#change the flat list image we have messed around with back to standard list of lists
		temp_row=flat_list_image[(k*col):((k+1)*col)]
		encoded_image.append(temp_row)
		temp_row = []
	save_image(encoded_image)		#saves the image
	
def extract_message():
	image = choose_png("Select the original image where a secret message is hidden. ")
	if len(image) == 0:
		msgbox("No image to extract. ")
		exit()
	row = len(image)
	col = len(image[0])
	flat_list_image = []
	for i in range(row):								#change a list of lists to a flat list
		flat_list_image.extend(image[i])
	p = (image[0][0]*image[0][1]*image[0][2]) % 15		#position coefficient
	message = ""									#creates an empty str where we will add characters later on
	decode = True									#intial condition for decoding
	j=0
	while decode:
		n = ((flat_list_image[3*(p+15*j+1)])%10)*100+((flat_list_image[3*(p+15*j+1)+1])%10)*10+((flat_list_image[3*(p+15*j+1)+2])%10)		#extrat the ASCII code hidden in secret pixels
		if n < 257:				#check we didn't put a "STOP" sign there
			message += chr(n)		#attach that character to the message str
			j += 1
		else:						#where we did put a "STOP" sign
			decode = False			#stops the decoding process because we have got the full message.
	save_text(message)				#saves the str into a .txt file

# main program

op_dict = { "a. Hide a message in an image" : "hide_message()",
		  "b. Extract a message from an image" : "extract_message()",
		  "c. Exit program" : "exit()"
		} 
	
image = []
while True:
	exec op_dict[choicebox("Choose an action: ","",op_dict.keys())]
	
