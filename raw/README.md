#Messenger
----------------------INFO-------------------------------------------------------------------------------------------\
App was created to provide security in social communications. \
How works all of algorithms of encryption: \
Let's imagine real situation, then it will be easier to understand
1) Creating user token:\
a) Why it needs ? It's your way to authorize in your dialog. User token
consists of 9 * 5 different characters,
which makes it difficult to select an encryption token.\
b) To create token you need username and password, that you can take from admin. BUT
it's necessary to say that ALL usertokens hasn't any links on your account and it's
really good.\
c) And if we still remember about deleting data every hour,
 then this makes the user token almost completely crypto-resistant (more about after)
2) Creating dialog:\
Dialog has links on user's tokens and on messages. Also dialog contains
user's hash sum (it's depends on user's IP, more after). The dialogue itself is 
announced by token that similar to user token.
3) Sending message:\
a) It's required to use additional app to pre-encrypt your message.
 (This is one of this,
  also you can write your own app with raw requests on server, more after)\
b) After encryption of your message it'll deliver your message on server.\
c) On server: 1) Checks your user's token. 2) Calculates your user's hash sum
via your IP. 3) Encrypts your message again with your hash sum and hash sum of your
interlocutor.\
And only then saves in database.\
d)The encryption scheme is similar to this:\
Raw user message --app--> encrypted user message level 1 --server--(checks user token,
 dialog token and hash sum amount obtained using IP)--> encrypted message level 2 -->
  saves message 
4) Getting message:\
User Token, Dialog Token (IP) --> Server -- (validates input data) -->
decrypts messages at level 2 --> returns encrypted messages of the first level
 --app --> decrypts messages in raw messages.
5) Every hour (UTC+0) all data except usernames and passwords is deleted.

----------------------APP--------------------------------------------------------------------------------------------\
App provides user interface to interact with server part of messenger and
 level one of message encryption. Also I tried to make it as convenient 
 as possible and comfortable for everyone.

 1) App was written on python and it's required some python libraries and python 
 itself.\
 Installation:\
 a) Please download python from https://python.org\
 b) Install python with adding it in PATH variable
 с) If you use raw module, open your console and install some libraries: (Write that in console)\
pip install requests\
pip install configparser\
pip install json\
pip install asyncio\
(In windows, in another OS it may be different)\
2) Set the settings in settings.ini or create this file if doesn't exist.\
[SERVER]\
IP =            213.226.112.85  #IP of server nowdays it is 213.226.112.85\
PORT =          8000 # PORT of server, 8000\
[AUTH] # You can set your Username and Password here, but it is not required \
USERNAME =  \
PASSWORD =       
[APP]  # Autolog provides auto log your commands and outputs in logfile \
AUTO_LOG =      True\
LOGFILE =       applog.log
3) Usage and some info:\
Run main.exe or main.py, then you will see command interface of program.
Short help you can see when wrote 'help'.
Some details I try to describe here.\
All commands are approximately similarя to this:\
 $Items$ $command$ $arg1(most often a name)$ $arg2$\
About comfort: the whole application is built on names under which many parameters are hidden.
You can change, delete these names and parameters of these objects.\
Here is detailed description of all these commands\
----UserToken----:\
Provides work with user token.\
a) UserToken create $name$ | Creates new user token with name $name$. You will use it after
 that to indicate a token. It sends request on server and returns created token,
  USERNAME and PASSWORD are required\
  For ex: UserToken create mynewtoken\ 
 b) UserToken add $name$ $token$ | This is similar to the previous command, but unlike it is not
 sends request on server. It creates token locally. This is necessary if you created a token
and forgot to save the session or if you created it in another application (or raw request),
but you need to initialize it. $name$ - name in namespace, $token$ - token\
For ex: UserToken add mynewtoken 123456789-qwertyuio-ASDFGHJKL-987654321-HELLOqwer\
c) UserToken rename $lastname$ $newname$ | Renames token in namespace usage\
For ex: UserToken rename mynewtoken myoldtoken
d) UserToken delete $name$ | Clears namespace from token name\
For ex: UserToken delete myoldtoken\
----DeleteInfo----:\
It's only one command that displays seconds before data cleaning.\
DeleteInfo | Displays time in seconds before delete\
----Dialog----:\
Provides work with dialogs.\
a) Dialog init $usertokenname$ $dialogname$ | Locally initializes dialog. It creates
some relations between usertoken and dialog and initializes basic parameters of dialog.\
For ex: Dialog init myusertoken newdialog\
b) Dialog create $dialogname$ | It sends request on server and creates dialog there.
(When use dialog init you only creates dialog in app, you can set some parameters and
only then create it on server). It displays your dialogue token, which is needed to create
communication between you and your interlocutor. \
For ex: Dialog create newdialog\
OUTPUT: XXXXXXXXX-XXXXXXXXX-XXXXXXXXX-XXXXXXXXX-XXXXXXXXX\
c) Dialog connect $dialog$ $token$ | Connects you to your interlocutor which created
dialog via dialog create command\
For ex: Dialog connect mydialog XXXXXXXXX-XXXXXXXXX-XXXXXXXXX-XXXXXXXXX-XXXXXXXXX\
d) Dialog sendmessage $dialog$ $message...$ | Sends encrypted (check next paragraph)
message on server. All words after $dialog$ will be delivered. 
All symbols allowed beside '~' and '^'\
 For ex: 'Dialog sendmessage mydialog hello world | will deliver message 'hello world' on server.\
e) Dialog setpassword $dialog$ $password$ | It sets password which uses in local encryption
and decryption (raw message --> encrypted message level 1; described in INFO.3). 
Non-repeating characters of the English alphabet are allowed.
 The register is not affected.\
For ex:\
 Dialog setpassword dialog key\
Dialog sendmessage dialog hello world | Will deliver on server message 'idppo ypwpb'
 ('hello world' with encryption based on word 'key') \
f) Dialog getmessages $dialog$ | Displays and logs (if turned on; more about in point 'j') all messages
 which takes from the response from the request to the server in format:\
time $target or me$ :~ message | 'target' it's name that you can change by Dialog settargetname
command (point 'i') \
For ex: Dialog getmessages mydialog\
OUTPUT:\
2020-04-28T12:06:36.534Z me :~hello\
2020-04-28T12:06:56.995Z target :~hi!\
g) Dialog getunreadmessages $dialog$ | This is the same as in the previous paragraph,
 but displays only new messages\
h) Dialog messages $dialog$ | Displays all messages which was already received by getmessages commands\
i) Dialog settargetname $dialog$ $name$ | Sets target name which we can see in getmessages commands outputs
 or in logs
 For ex:\
 Dialog settargetname dialog myfriend\
 Dialog getmessages dialog\
 OUTPUT:\
 2020-04-28T12:06:36.534Z me :~hello\
 2020-04-28T12:06:56.995Z myfriend :~hi!\
j) Dialog autolog $dialog$ $bool$ | Sets autolog parameter of dialog. If true:
When you getting messages via getmessages commands it will log all messages in
 $created_time_of_dialog$$dialog_name$.log file\
k) Dialog reloadmessages $dialog$ | Reboot all your messages. It is necessary when you
set an incorrect password or changed the name of the target. (When you getting messages
from getmessages commands, it only appends new messages in dialog messages (without
recryption and renaming of target of already received messages))\
l)Dialog logmessages $dialog_name$ | Logs messages in 
$created_time_of_dialog$$dialog_name$.log file 
m) Dialog rename $lastname$ $newname$ | Similar on UserToken rename command\
n) Dialog delete $dialog$ | Similar on UserToken delete command\
o) Dialog addtoken $dialog$ $token$ | Use it if you already created or connected to dialog
but left from the program.
p) Dialog interactive $dialog$ | Activates interactive mode.
All that you will wrote will be delivered to target. And every 4 seconds checks unread messages
and displays them. This is similar to the usual messenger that we used to see.
To understand better try it. To exit write '$EXIT$' (with dollars).
----Sessions----:\
It provides sessions. You can save your dialog and user tokens to use them later.
It saves them in file with name $name$session.py. When load it please do not specify
the '...session.py'. only name! \
a)Session save $name$ | Saves current session in file\
b)Session load $name$ | Loads session from file\
c)Session clear | Deletes all current dialogs and user tokens from namespace\
d)Session fullclear | 'Session clear' + Deletes app log and messages logs if exist 

----------------------API--------------------------------------------------------------------------------------------\
use it to get UserToken (in content: UserToken) \
/api/newtoken  POST Headers:{'USERNAME': ... , 'PASSWORD': ... }

use it to create new DialogToken (in content: DialogToken) \
/api/newdialog POST Body:{'UserToken': ... }

use it to accept the created dialog\
/api/acceptdialog POST Body:{'UserToken': ... , 'DialogToken': ... }

use it to send message in dialog \
/api/sendmessage POST Body:{\
'UserToken': ... , 'DialogToken': ... , 'MessageText': ... }

use it to get Messages from dialog (in content: Messages) \
/api/getmessages GET Params:{'UserToken': ... , 'DialogToken': ... }

use it to get time to delete data (seconds, in content: TimeDeleteInfo)
/api/getinfo GET

----------------------EXAMPLES---------------------------------------------------------------------------------------\
Quick example of trying to chat with your friend (Y - command which is entered by you, F - by friend;
S - small interactive :D ):\
Y:\
UserToken create user\
Dialog init user dialog\
Dialog setpassword dialog hey\
Dialog settargetname dialog friend\
Dialog create dialog\
OUTPUT: ECFOPVFGK-DWUCOBTMG-791161392-GVUFRIVVB-STHOEVDGI\
F:\
UserToken create me\
Dialog init me mydialog\
Dialog connect mydialog ECFOPVFGK-DWUCOBTMG-791161392-GVUFRIVVB-STHOEVDGI\
Y:\
Dialog sendmessage dialog hello! my friend!\
Dialog getmessages dialog\
OUTPUT:\
2020-04-28T12:13:35.834Z me :~hello! my friend!\
F:\
Dialog getmessages mydialog\
OUTPUT:\
2020-04-28T12:13:35.834Z target :~idktp! nx esjdmj!\
S: Friend (?????? what the ****?) - The answer is setting password!\
Dialog setpassword mydialog hey\
Dialog getmessages mydialog\
OUTPUT:\
2020-04-28T12:13:35.834Z target :~idktp! nx esjdmj!\
S: Friend ??? - You need to reload your messages!\
Dialog reloadmessages mydialog
Dialog getmessages mydialog
OUTPUT:\
2020-04-28T12:13:35.834Z target :~hello! my friend!\
Dialog sendmessage mydialog hi!\
Y:\
Dialog getmessages dialog\
OUTPUT:\
2020-04-28T12:13:35.834Z me :~hello! my friend!\
2020-04-28T12:13:40.945Z friend :~hi!

---------------------------------------------------------------------------------------------------------------------\
Some additional words about the security: If you really care about security 
and you need to send quick protected message don't log
your messages, don't log your applog and don't set password and username in settings.ini,
You can set them at every entrance. And don't use sessions.
Due to the fact that someone can penetrate your computer files from the inside.

Thank you for using my service. 04/28/2020 mm-dd-yyyy