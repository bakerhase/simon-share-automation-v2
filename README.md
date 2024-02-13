# simon-share-automation-v2
## Install
Three things are required for this program to work properly
1. Change the "clientID" and "clientSecret" variables in mediaPublisher.java to your API instance's client ID and secret ID
2. Recompile mediaPublisher.java (i.e. run "javac mediaPublisher.java")
3. Export a v1 type Sections csv from Echo, rename the file "sections.csv", and place it in the same directory that the program will run from
4. (As of right now you will also need to directly edit the reference to the term name in a function in "share-automation.py", I will be changing this to work differently at some point)

## Usage
1. Enter your UR NETID and password in the respective field in the GUI (this is only actually necessary if you are also assigning classes to professors)
2. Enter the URLs for each Echo capture you wish to publish on a new line in the URL field
3. Check any optional check boxes that you want (the first time you run the program, be sure to check the "Also update term info" box)
4. Hit the "assign" button
5. Double check to make sure each class was published properly, assigned properly, etc.
Any errors should pop out in the terminal, though the terminal output is probably not particularly easy to parse through as of now
