import json									# Handle Json Objects
import requests								# Website requests
import webbrowser							# My Hyperlink
import tkinter as tk						# Entire Window
from tkinter import ttk						# Entire Window
from PIL import Image, ImageTk				# Logo
from collections import defaultdict			# Dict
from datetime import datetime, timedelta	# Time Formating

global Table			# Table where everything is shown
global StateBox			# Top Message Box
global RequestSession 	# Our Request Session

def open_link(event):
    webbrowser.open("https://github.com/Rel09/42Time")
def calculate_monthly_time_logged(data):
	'''
	Big math
	'''
	monthly_total = defaultdict(int)
	for date_str, time_str in data.items():
		month = date_str[:7]
		hours, minutes, seconds = map(int, time_str.split(':'))
		total_seconds = hours * 3600 + minutes * 60 + seconds
		monthly_total[month] += total_seconds
	for month, total_seconds in monthly_total.items():
		hours, remainder = divmod(total_seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		monthly_total[month] = f'{hours:02}:{minutes:02}:{seconds:02}'
	return dict(monthly_total)
def login(username, password):
	'''
	Logging on the Intra without using the API
	'''
	global RequestSession
	# Init Requests -> Since we dont use 42api, we log on intra ourselves
	RequestSession = requests.Session()

	# Get on the Intra Login Page
	response = RequestSession.get("https://profile.intra.42.fr/")
	if response.status_code != 200:
		return 0
	
	# Get the Submit Button Post Message (i wanted to do it without using any external library)
	action_value = ""
	action_start = response.text.find('action="')
	if action_start != -1:
		action_end = response.text.find('"', action_start + len('action="'))
		if action_end != -1:
			action_value = (response.text[action_start + len('action="'):action_end]).replace("amp;", "")	# Remove the garbage from Post Message

	# If we didn't found the Submit Button, Break
	if (action_value == ""):
		return 1

	# Send the Post Request
	response = RequestSession.post(action_value, data= { 'username' : username, 'password' : password })

	# Intra always return 200, only god know why, this handle it
	if "Invalid username or password" in response.text:
		return 2

	# Grab Cluster Data
	Cluster = RequestSession.get(f"https://translate.intra.42.fr/users/{username}/locations_stats.json")
	if Cluster.status_code != 200:
		return 3

	# Remove the digits after seconds since we dont need em
	result = json.loads(Cluster.text)
	for key, value in result.items():
		result[key] = value.split(".")[0]

	# Convert Everything to Json for display
	return json.dumps(calculate_monthly_time_logged(result), indent = 4)
def hideInputs():
	'''
	Hide the Textboxes ( disabled while logging in )
	'''
	# Hide everything related to Username
	username_entry.pack_forget()
	username_label.pack_forget()

	# Hide everything related to Password
	password_entry.pack_forget()
	password_label.pack_forget()

	# Hide the button
	submit_button.pack_forget()
	root.update()
def showInputs():
	'''
	Show the Textboxes ( disabled while logging in )
	'''
	# Show everything related to Username
	username_entry.pack()
	username_label.pack()

	# Show everything related to Password
	password_entry.pack()
	password_label.pack()

	# Show the button
	submit_button.pack()
	root.update()
def showMessage(message):
	'''
	Edit the Top Header Text
	'''
	global StateBox
	StateBox.config(text=message)
	root.update()
def display_table(data):
	'''
	This display the times in the Table
	'''
	global Table
	data = json.loads(data)
	Table = ttk.Treeview(root, columns=("Date", "Time"), show="headings")
	Table.heading("Date", text="Month")
	Table.heading("Time", text="Time")
	Table.pack(padx=20, pady=20)

	for date, time in data.items():
		Table.insert("", "end", values=(date, time))
def alreadyLoggedSubmit():
	'''
	Submit Button Event (Already Logged)
	'''
	global Table
	global RequestSession
	Table.destroy()

	# Send Post Data
	Cluster = RequestSession.get(f"https://translate.intra.42.fr/users/{username_entry.get()}/locations_stats.json")
	if Cluster.status_code != 200:
		return 0

	# Return as Json Objects, remove the digits after seconds since we dont need em
	result = json.loads(Cluster.text)
	for key, value in result.items():
		result[key] = value.split(".")[0]
	resultdict = calculate_monthly_time_logged(result)
	display_table(json.dumps(resultdict))
def submit():
	'''
	Submit Button Event (Not logged at all)
	'''
	hideInputs()
	showMessage("Attempting to login ...")

	# Post Message
	data = login(username_entry.get(), password_entry.get())
	# Error Handling
	if data == 0 or data == 1 or data == 2 or data == 3:
		# Couldnt get on Intra website
		if data == 0:
			showMessage("Intra is down")
		# Couldnt find the Submit button
		elif data == 1:
			showMessage("Couldnt Log on Intra")
		# Wrong Username / Password
		elif data == 2:
			showMessage("Wrong credentials")
		showInputs()
	
	# Display Data
	else:
		showMessage("Logging Successful")
		username_label.pack()
		username_entry.pack()
		NewRequestButton = ttk.Button(root, text="Submit", command=alreadyLoggedSubmit)
		NewRequestButton.pack()
		display_table(data)
		#print(data)

if __name__ == "__main__":
	global StateBox

	# Create the main window
	root = tk.Tk()
	root.title("")

	# Background Image
	background_image = ImageTk.PhotoImage(Image.open("42qc.png"))

	# Create a label to hold the background image
	background_label = tk.Label(root, image=background_image)
	background_label.place(relwidth=1, relheight=1)

	# Window Size
	window_width = 700
	window_height = 800

	# Get Screen Size
	screen_width = root.winfo_screenwidth()
	screen_height = root.winfo_screenheight()

	# Center the Window
	x_position = (screen_width - window_width) // 2
	y_position = (screen_height - window_height) // 2

	# Set the window position
	root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

	# Make the window non-resizable
	root.resizable(False, False)

	# Status Box
	StateBox = tk.Label(root, text="Enter your Intra info", font=("Arial Black", 16) )
	StateBox.pack()

	# Username Textbox
	username_label = tk.Label(root, text="Username:")
	username_label.pack()
	username_entry = ttk.Entry(root, justify="center")
	username_entry.pack()

	# Password Textbox
	password_label = tk.Label(root, text="Password:")
	password_label.pack()
	password_entry = ttk.Entry(root, justify="center", show="*")  # Show * for password entry
	password_entry.pack()

	# Submit Button
	submit_button = ttk.Button(root, text="Submit", command=submit)
	submit_button.pack()

	# Hyperlink
	hyperlink_label = tk.Label(root, text="Visit the Repo", fg="blue", cursor="hand2")
	hyperlink_label.pack(side="bottom", padx=10, pady=10)

	# Bind the label to a function when clicked
	hyperlink_label.bind("<Button-1>", open_link)

	# Bring the window to the front
	root.lift()
	root.attributes('-topmost', True)

	# Start Loop
	root.mainloop()
