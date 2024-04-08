# simon-share-automation-v2
## Install
Several things are required for a first time install. If I get real bored, maybe I'll make this process easier.
1. Download the java version of the Echo360 SDK (see https://support.echo360.com/hc/en-us/articles/360038693311-EchoVideo-API-and-SDK-Documentation)
2. Extract the contents of "Echo360-JAVA_SDK_{version}" in the same directory that the program will run from
3. Copy an instance of "EchoLogger.class" to the directory the program will run from (it is included in every example in the SDK)
4. If you are not part of the SimonIT Help Desk (I doubt you aren't), then you will need to obtain an Echo360 API client and secret ID (see https://support.echo360.com/hc/en-us/articles/360035034252-EchoVideo-Generating-Client-Credentials-to-Obtain-Access-Token). If you ARE part of SimonIT, get the credentials from Baker.
5. Change the "clientID" and "clientSecret" variables in mediaPublisher.java to your API instance's client ID and secret ID
6. Recompile mediaPublisher.java (i.e. run "javac mediaPublisher.java") (this requires the java development kit to be installed, which is bad on my part. Maybe I'll fix that if I get bored)
7. Export a v1 type Sections csv from Echo, rename the file "sections.csv", and place it in the same directory that the program will run from (see https://support.echo360.com/hc/en-us/articles/360035405251-EchoVideo-Using-Imports-Exports-and-CSV-Files)
8. The first time you run the program, check the "Also update term?" box and enter the term name (e.g. Spring 2024) in the "Term name (if updating term)" field

## Usage
1. Enter the URLs for each Echo capture you wish to publish on a new line in the URL field
2. Hit the "Submit for Upload Process" button
3. Wait for "Done!" to pop up under the button
4. Double check to make sure each class was published properly in Echo.

Any errors should pop out in the terminal, though the terminal output is probably not particularly easy to parse through as of now. If you encounter any errors, check to see which URL was the first URL in the list to not be published in Echo, exclude that URL, and try again.

## Updating term
At the start of each new term (including changes from e.g. Fall A to Fall B), follow theese steps:
1. Export a v1 type Sections csv from Echo, rename the file "sections.csv", and place it in the same directory that the program will run from (see https://support.echo360.com/hc/en-us/articles/360035405251-EchoVideo-Using-Imports-Exports-and-CSV-Files). This will replace the previous sections.csv in the directory, that is okay.
2. The next time you run the program, check the "Also update term?" box and enter the term name (e.g. Spring 2024) in the "Term name (if updating term)" field

Note that the directory the program runs from is not the same as the directory which the shortcut to the program is in.
