# All required packages come with python by default (tkinter) or from selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
import webdriver_manager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import tkinter as tk
import tkinter.messagebox
import subprocess
import csv

#checks if a given email is an admin email from a list of emails (ultimately should be modified to be from a text file containing amin emails)
def isAdminEmail(email):
    adminEmails = ["list",
                   "of",
                   "admin",
                   "emails"]
    isAdmin = False
    for adminEmail in adminEmails:
        if email == adminEmail:
            isAdmin = True

    return isAdmin


# gets the instructor email from the csv info row
def get_instructor_from_row(row_list):
    instructors = row_list[11]
    emailList = instructors.split(";")
    tgtEmail = ""
    for email in emailList:
        if isAdminEmail(email)==False:
            tgtEmail = email
            break
    return tgtEmail


#gets information from the csv row in order to format a title for the course section (e.g. MKT321.12)
def get_title_from_row(row_list):

    codeFieldVal = row_list[2]

    if len(codeFieldVal)>3:
        course_code = row_list[2][0:3]
    else:
        course_code = row_list[2]

    course_section = row_list[6]
    section_title = course_code+course_section
    return section_title

# For a given target term, parse through a file (sections.csv) that is exported from echo in order to make a file config.txt which contains sectionIds and professor emails for each course
def update_term_data(target_term):
    try:

        sectioncsv = open("sections.csv", newline="")
        sectionreader = csv.reader(sectioncsv, delimiter=",")

        #target_term = "Spring 2024"#input("What is the target term? ")

        dict_rows = []
        for row in sectionreader:
            if row[5] == target_term:
                section_title = get_title_from_row(row)
                sectionId = row[0]

                instructorEmail = get_instructor_from_row(row)

                dict_rows.append(section_title.upper()+","+sectionId+","+instructorEmail)

        configfile = open("config.txt", "w")
        configfile.write("term,"+target_term+"\n\n")
        for outrow in dict_rows:
            configfile.write(outrow+"\n")

        configfile.close()
    except:
        print("Problem updating term data. Does sections.csv exist?")

# This function will need to be changed if Echo360 changes the format of their URLs of media pages
# Takes a list of URLs to media pages, and returns a string of mediaIDs in a format that can be passed to java scripts in the shell
def mediaIdFromURLs(urlList):
    idString=''
    for url in urlList:
        qMarkIdx = url.find("?")
        baseIdx = url.find("echo360.org/media/")
        startIdx = baseIdx+18
        mediaId = url[startIdx:qMarkIdx]
        idString+=mediaId
        idString+=" "

    # remove extra space at the end
    idString = idString[0:len(idString)-1]

    return idString

# Passed in the title of an echo recording page, returns a string of the total course number (e.g. CIS442.31B)
def titleparse(page_title):
    endidx = page_title.index("'")
    reverse_title = ''
    flag = 0
    idxadd = -1
    while flag == 0:
        if page_title[endidx+idxadd] == ' ' or (endidx+idxadd) == -1:
            flag = 1
        else:
            reverse_title+=page_title[endidx+idxadd]
            idxadd += -1

    course_title = reverse_title[::-1]
    return course_title

# Main function which opens and fills information for classes in Google Chrome
# Passed in a URAD username and password, as well as a list of URLs for the desired classes
def assign_to_owner(uname, pwrd, urllist):
    # All the data that is necessary for the script at current moment.
    usremail = uname+'@u.rochester.edu'# ASSUMES AD USERNAME IS THE SAME AS EMAIL ADDRESS. CORRECT ASSUMPTION?
    usrname = uname
    passwrd = pwrd
    tgtURL = "https://echo360.org/home"

    # Gets term name from config.txt. See comment at the top of the script for notes on format of config.txt
    config_file = open('config.txt', 'r')
    termline = config_file.readline()
    config_file.close()
    termidx = termline.index(',')
    termstop = termline.index('\n')
    term = termline[termidx+1:termstop]

    # Makes it so the window stays open after program execution
    firefox_options = Options()
    #firefox_options.add_experimental_option("detach",True)


    #cwd = os.getcwd()

    # Starts webdriver service
    service = FirefoxService(executable_path=GeckoDriverManager().install())
    global driver
    driver = webdriver.Firefox(service=service, options = firefox_options) #option call also needed for persistent window
    driver.get(tgtURL)


    # Enters email into Echo login page
    email_field = driver.find_element(by=By.ID, value = "email")
    email_field.send_keys(usremail)
    submit_button = driver.find_element(By.ID,value='submitBtn')
    submit_button.click()

    # This line sets the amount of time the driver waits to be 30 seconds.
    # Making this time too short introduces problems with the try/except
    # statement, see later comment
    driver.implicitly_wait(30)

    # Enters active directory username and password into UR login page
    uname_field = driver.find_element(By.ID, "usernamevis")
    pwrd_field = driver.find_element(By.ID, "password")
    logon_button = driver.find_element(By.ID, "log-on")

    uname_field.send_keys(usrname)
    pwrd_field.send_keys(passwrd)

    # specifically navigates the dropdown menu
    domain_select = driver.find_element(By.ID, "domain")
    d_select = Select(domain_select)
    d_select.select_by_value("@ur.rochester.edu")

    logon_button.click()


    # While loop prevents the rest of the script from running until properly on the Echo site
    title = driver.title

    # This while loop identifies the Echo dashboard page by the title being 'Home' and no other
    # page brought up by DUO authentication having 'o' as the second character in the title. If
    # either system is changed so that this is no longer the case, this block will need to change
    while len(title)<2 or title[1] != 'o': # Length requirement prevents error if title is an empty string
        title = driver.title

    # Loops over each URL in the given URL list
    for URL in urllist:
        # this try statement lets the program continue to good URLs if it encounters a problem.
        # It also behaves strangely with the implicit wait. If the implicit
        # wait is too short, I believe that the try statement assumes that
        # the commands have excepted out after the implicit wait time before completing the entire try statement
        # 30 seconds seems to be a fine amount of time, shorter might also be okay
        # There is almost certainly a better way to resolve this issue
        try:
            # Makes new tab
            driver.switch_to.new_window('tab')
            driver.get(URL)


            title = driver.title
            # Takes course name from title of webpage to later pass into fields

            total_coursename = titleparse(title)


            ### This entire block would be better as a function, I think, but I am not yet aware of how to pass a webdriver
            # Searches a config.txt in order to return the email of the professor
            # and assign to the professor in the "Details" tab. Requires a dictionary of professor emails to be maintained
            # each term in order to function. See comment at top of this script for notes on the format of config.txt
            prof_email = ''
            config_file = open('config.txt', 'r')
            config_lines = config_file.readlines()
            for email_line in config_lines[2:]:
                lineList = email_line.split(",")
                if total_coursename.upper() == lineList[0]:
                    prof_email = lineList[2]
            config_file.close()

            # Clicks to Permissions subtab

            #As far as I can tell XPATH is the only way to uniquely identify this element. That sucks. Too bad.
            #Maybe CSS selector would be better? "button.sc-hMFtBS:nth-child(5)"
            permissions_subtab_button = driver.find_element(By.XPATH, "/html/body/div[3]/div[2]/div[3]/div/div/div/div[1]/div/button[5]")
            permissions_subtab_button.click()

            zoom_flag = False #defaults to false just in case

            default_assignment_field = driver.find_element(By.CSS_SELECTOR, "span.OwnerControls__StyledSpan-uu0jzw-4.hmRsjL")
            default_assignment = default_assignment_field.get_attribute("title")
            if "Zoom" in default_assignment:
                zoom_flag = True
            elif "zoom" in default_assignment:
                zoom_flag = True

            if (prof_email != '') and zoom_flag:
                # Click change owner button
                change_owner_button = driver.find_element(By.ID, 'change-owner-open')
                change_owner_button.click()

                # Access the dropdown
                owner_dropdown = driver.find_element(By.ID, 'change-owner-select_input')
                owner_dropdown.click()

                # Pass professor email into dropdown field
                owner_dropdown_input = driver.find_element(By.XPATH, '''//*[@id="react-select-2-input"]''')
                owner_dropdown_input.send_keys(prof_email)

                #owner_box = driver.find_element(By.CLASS_NAME, "css-1g6gooi")
                #owner_box.send_keys(Keys.RETURN)
                #owner_dropdown_input.send_keys(Keys.RETURN)
                owner_dropdown_item = driver.find_element(By.XPATH , "//*[contains(text(),'<"+prof_email+">')]")
                owner_dropdown_item.click()

                # Click done
                done_button = driver.find_element(By.ID, 'change-owner-done')
                #owner_dropdown_input.send_keys(Keys.RETURN)
                #driver.implicitly_wait(300000000)
                done_button.click()
        except:
            print("Issue with URL "+URL)

def publish_classes(urlShellString):
    #Just runs the command specified in the shell. Pretty based solution to my problem of integrating java
    subprocess.run("java mediaPublisher "+urlShellString, shell=True)


# Performs the functions of the 'submit' button. Deletes values in entries of the GUI
# Calls script passing in the user-entered URAD credentials and URL list
def submitHandler():
    upVal = updateValue.get()
    asVal = assignValue.get()
    uname = uname_entry.get()
    pwrd = pwrd_entry.get()

    urlEntry = URL_box.get("1.0", tk.END)
    print(urlEntry)
    while urlEntry[-1]=="\n":
        urlEntry = urlEntry[0:len(urlEntry)-1]

    print(urlEntry)
    urllist = urlEntry.split("\n")
    """
    # Formats each URL with a space in between them to pass to a shell command later
    urlString = urlEntry.replace("\n"," ")

    urllist = []
    entry = ''
    stopidx = len(urlString)-1
    idx = 0
    for elt in urlString:
        if elt != ' ':
            entry+=elt
            if idx+1 == stopidx:
                urllist.append(entry)
        elif elt ==' ' and idx != stopidx:
            urllist.append(entry)
            entry=''
        elif elt == ' ' and idx ==stopidx:
            continue

        idx+=1
    """
    shellString = mediaIdFromURLs(urllist)
    print("Publishing IDs "+shellString)

    if upVal==1:
        update_term_data("Spring 2024") #THIS SHOULD NOT BE HARD CODED, CHANGE THIS ASAP

    if asVal==1:
        assign_to_owner(uname, pwrd, urllist)


    publish_classes(shellString)

    uname_entry.delete(0, tk.END)
    pwrd_entry.delete(0,tk.END)
    advisory_label["text"]='Done!'


# Generates GUI window
window = tk.Tk()
window.title("Zoom Recording Share Automation")
#window.withdraw() #hides main window until Read me is addressed

# Labels and creates username entry field
uname_label = tk.Label(text='AD User')
uname_entry = tk.Entry(fg='black', bg='white', width = 50)

# Labels and creates password entry field
pwrd_label = tk.Label(text='AD Password')
pwrd_entry = tk.Entry(fg='black', bg='white', show = '*', width = 50)

# Labels and creates URL entry text box
URL_label = tk.Label(text = 'Start each class recording URL on a new line')
URL_box = tk.Text() #Play with text wrapping. Is it better for no wrapping? Will that be confusing? Will having text wrapping be confusing?

#Labels and creates submit button
submit = tk.Button(window, text='Submit for Upload Process', command=submitHandler)


#Assign to professor checkmark

assignValue = tk.IntVar()
assign_check = tk.Checkbutton(window, text="Also assign to professor?", variable=assignValue, onvalue=1, offvalue=0)

# Update term data checkmark

updateValue = tk.IntVar()
update_check = tk.Checkbutton(window, text="Also update term?", variable=updateValue, onvalue=1, offvalue=0)




advisory_label = tk.Label(text = ' ')



# Adds GUI elements to the window
uname_label.pack()
uname_entry.pack()
pwrd_label.pack()
pwrd_entry.pack()
URL_label.pack()
URL_box.pack()
submit.pack()
advisory_label.pack()
update_check.pack()
assign_check.pack()
config_file = open('config.txt', 'r')
termline = config_file.readline()
config_file.close()
termidx = termline.index(',')
termstop = termline.index('\n')
term = termline[termidx+1:termstop]

# Shows a READ ME box giving info on the state of the app and some disclaimers
#tk.messagebox.showinfo(title = 'READ ME', message = 'The currently selected term is: '+term+'.\nIf this term is incorrect, please update the "term:" field in the config file.\n\nUPDATE AS OF 9/26/23\n\u2022This app now throws up error messages if there are problems with a URL.\n\u2022It uses Firefox instead of Chrome now, as God intended.\n\u2022This script now depends on "exception_courses.txt." Nothing bad will happen if the script is not present, it just may not work for all courses. See github for formatting of the file.\n\u2022Be sure to DOUBLE CHECK any and all auto-filled information. I take no responsibility for any errors in shared class information as a result of usage of this app.\n\u2022If you find any bugs, please notify Baker either in person or at bhase@u.rochester.edu.\n\u2022You can find the source code on my GitHub, github.com/bakerhase.\n\u2022This app stores no information on your AD Credentials.\n\u2022For further usage instructions, please see "INSTRUCTIONS.PDF"')
#window.deiconify() #shows the main app window once the Read Me has been addressed


window.mainloop()



