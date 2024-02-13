import com.echo360.sdk.Echo360Api;
import com.echo360.sdk.model.objects.MediaAccessLink;
import com.echo360.sdk.model.objects.MediaShare;
import com.echo360.sdk.model.requests.ListRequest;
import com.echo360.sdk.model.objects.Media;
import com.echo360.sdk.services.MediaService;
import com.echo360.sdk.util.Echo360Exception;
import com.echo360.sdk.services.LessonService;
import com.echo360.sdk.model.objects.Lesson;
import com.echo360.sdk.model.requests.AuthRequest;
import java.io.*;


public class mediaPublisher{
    private static String baseUrl = "https://echo360.org";
    private static String clientID = "YOURCLIENTIDHERE"
    private static String clientSecret = "YOURCLIENTSECRETHERE";
    private static EchoLogger logger;


    //Takes the "mediaName" field from the media on the server and returns the section name in a SimonIT-familiar format (e.g. MKT111.12)
    static String titleParse(String mediaName){
        //splits the media name into an array of strings based on where the spaces are
        String[] splitName = mediaName.split(" ", -1);
        String word = null;
        String sectionName = null;

        //Checks each word in that array for a comma, uses that comma to identify where the section name is, since all media have "<sectionName>'s Zoom Room" in their title
        for (int i=0; i<splitName.length; i++){
            word = splitName[i];
            if (word.indexOf("'")!=-1){
                sectionName = word.substring(0,word.length()-2);
            }
        }
        return sectionName;
    }

    //Checks through a .txt file to find the sectionId for the given sectionName (e.g., MKT222.23 corresponds to sectionId xx123-456)
    static String getSectionId(String sectionName){
        String tgtSection = sectionName.toUpperCase();
        String inputLine = null;
        String sectionId = null;
        Boolean stopFlag = false;
        try{
            FileReader input = new FileReader("config.txt");
            BufferedReader bufRead = new BufferedReader(input);
            while (!stopFlag){
                inputLine = bufRead.readLine();
                if (inputLine==null){
                    stopFlag = true;
                }else{
                    String[] splitLine = inputLine.split(",");
                    if (splitLine[0].equals(tgtSection)){
                        sectionId = splitLine[1];
                        stopFlag = true;
                }
                }
            }

        }catch (Exception e){
            System.out.println(e);
        }
        return sectionId;
    }

    //Takes the "createdAt" string from the media on the server and returns a date in the format we use (e.g. 01.01.1999)
    //createdAt takes the form "YYYY-MM-DD"+"THH:MM:SSZ"
    //CURRENTLY UNTESTED (should work)
    static String dateParse(String createdAt){
        String YY = createdAt.substring(2,4);
        String MM = createdAt.substring(5,7);
        String DD = createdAt.substring(8,10);
        String dateString = MM+"."+DD+"."+YY;
        return dateString;
    }

    // args is a list of mediaIds to do stuff to. These are parsed from the URLs of the media and passed to this script by the python code.
    public static void main(String[] args) {
        //Sets up a logger to log responses from the server
        logger = new EchoLogger();

        //I think declaring variables here is likely best practice. Too bad, you get one best practice.
        String mediaTitle = null;

        //Try statement is so that problems with the API calls can be caught. Don't really know if this is set up well. Probably not.
        try {
            //Initialize an API instance, and a "mediaService" and "lessonService" to manage (most) api calls pertaining to media and lessons
            Echo360Api echoSDK = new Echo360Api(baseUrl, clientID, clientSecret, logger);
            MediaService mediaService = new MediaService(echoSDK);
            LessonService lessonService = new LessonService(echoSDK);


            //Each element of args is a mediaId for a media to be published. Loops through them and publishes each.
            for (int i=0; i<args.length; i++){

                // Get title of the media
                String mediaId = args[i];
                logger.logString("Retrieving media information for mediaId: " + mediaId);

                //Get information about the media for the given mediaId
                Media media = mediaService.get(mediaId);

                //Checks that the media is publishable. Currently just breaks out of the for loop if a media is not publishable. There is a better way to do this I'm sure'
                if (!media.isPublishable){
                    System.out.println("Media not publishable for mediaId "+mediaId);
                    break;
                }

                //Gets the media title in order to parse the section name (e.g. MKT111.12) from the title
                mediaTitle = media.name;
                String sectionName = titleParse(mediaTitle);


                //Takes the section name and returns the sectionId from a .txt file
                String sectionId = getSectionId(sectionName);


                //Create a new lesson object belonging to the desired section. POST that lesson to the server
                Lesson lesson = new Lesson();
                lesson.sectionId = sectionId;
                Lesson serverLesson = lessonService.create(lesson);

                //Get information for various fields of the lesson
                String dateString = dateParse(media.createdAt);
                String captureId = media.captureOccurrenceId;
                String lessonName = "Zoom."+sectionName+"-"+dateString;

                //fills the fields of the client-side lesson object with the new data
                serverLesson.captureOccurrenceId = captureId;
                serverLesson.name = lessonName;
                serverLesson.timeZone = "US/Eastern";

                //update the lesson on the server
                Lesson updatedLesson = lessonService.update(serverLesson);

                //Get information about the lesson and about the API credentials to be able to publish the media to the newly created lesson
                String lessonId = updatedLesson.id;
                AuthRequest currentAuth = echoSDK.getCurrentCredentials();
                String token = currentAuth.access_token;

                //Make a raw API POST request to publish the media to the newly created lesson. Makes it immediately available
                echoSDK.ApiRequest("POST", "application/json", "Bearer "+token, "/public/api/v1/publish/media/"+mediaId+"/lessons/"+lessonId, "{\"available\": true}", true);

                System.out.println("***Media "+mediaId+" published to lesson "+lessonId+" in section "+ sectionId+" with title "+lessonName+"***");

            }


            }catch (Echo360Exception ex) {
            switch (ex.getErrorType()) {
                case "SERVER_ERROR":
                    logger.logString("Server Response [" + ex.getResponseCode() + "] Server Message: " + ex.getServerMessage());
                    break;
                case "INVALID_PARAMETER":
                    logger.logString("Invalid Input: " + ex.getMessage());
                    break;
                default:
                    logger.logString("[" + ex.getErrorType() + "] Error Message: " + ex.getMessage());
                }
            }

            }


    private static void printObject(Object current) {
        logger.logString("***************");
        logger.logString(current.toString());
        logger.logString("");
    }

}

