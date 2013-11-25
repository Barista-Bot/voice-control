This is the Barista Bot Voice control ROS Node 'voice_control'

It is split into several sub modules each with their own resposibilities and are contained in the scripts directory.

voice_control_server.py is the main ROS node which controls the voice interaction flow.

It is invoked using the service 'voice_control' which takes no input and returns a boolean indicating the success of the user interaction.

It communicates with the user identification node to identify and track users, recognizing if they have interacted with the system previously.  When the user identification system identifies that a user has not been visible for a short amount of time, it publishes and update to the 'user_identification/presence' where it receives a user identification 'msg' object containing:


is_person

is_known_person

user_id

confidence


The Modules:

flacrecord - Listens to the users voice and records it until they stop speaking, producing a flac audio file
googlewebspeech - Submits the flac file to the google web speech server and receives a JSON object of the speech google transcribed
witapi - Submits the heard speech to the wit.ai web api for processing. Receieves a JSON object containing the intent of the speech, and any entities contained within
responseprocess - Analyzes the return wit.ai result and decides what action/response should be given to the user dependant upon level of interaction
baristaDB - The persistent data of the voice interaction system. Contains setter and getter methods for database information.
	Information stored:
	User ID, Name, Interaction Level, Number of Visits, Date of last visit, Coffee Preference, Course Studied, Weather Conditions
googletext2speech - Submits a string to the google text 2 speech api and receives a wav file of the text spoken to be played back

Each module contains its own unit tests in the __main__ method.  Run the script itself to run these tests and validate functionality

void_control_client can be run with the voice_control_server running to initiate interaction.

There are also a number of easter eggs contained in the code which play audio samples when the phrases are recognized:


what does the fox say

do you have a license

do you work out

something strange in the neighborhood

attention

i'm talking to you

i don't want you

how did we meet

do you have any popcorn

how did you get to work today

which man are you

what are you

the dogs are out

what did she say

is there a house in new orleans

