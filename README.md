# simon-share-automation-v2
## Install
Several things are required for a first time install. If I get real bored, maybe I'll make this process easier.
1. Download the java version of the Echo360 SDK (see https://support.echo360.com/hc/en-us/articles/360038693311-EchoVideo-API-and-SDK-Documentation)
2. If you are not part of the SimonIT Help Desk (I doubt you aren't), then you will need to obtain an Echo360 API client and secret ID (see https://support.echo360.com/hc/en-us/articles/360035034252-EchoVideo-Generating-Client-Credentials-to-Obtain-Access-Token). If you ARE part of SimonIT, get the credentials from Baker.
3. Change the "clientID" and "clientSecret" variables in mediaPublisher.java to your API instance's client ID and secret ID
4. Recompile mediaPublisher.java (i.e. run "javac mediaPublisher.java") (this requires the java development kit to be installed, which is bad on my part. Maybe I'll fix that if I get bored)
5. Export a v1 type Sections csv from Echo, rename the file "sections.csv", and place it in the same directory that the program will run from (see https://support.echo360.com/hc/en-us/articles/360035405251-EchoVideo-Using-Imports-Exports-and-CSV-Files)
6. (As of right now you will also need to directly edit the reference to the term name in a function in "share-automation.py", I will be changing this to work differently at some point)

## Usage
1. Enter your UR NETID and password in the respective field in the GUI (this is only actually necessary if you are also assigning classes to professors)
2. Enter the URLs for each Echo capture you wish to publish on a new line in the URL field
3. Check any optional check boxes that you want (the first time you run the program, be sure to check the "Also update term info" box)
4. Hit the "assign" button
5. Double check to make sure each class was published properly, assigned properly, etc.
Any errors should pop out in the terminal, though the terminal output is probably not particularly easy to parse through as of now
