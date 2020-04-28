import configparser
import datetime
import asyncio
import os
import client.Server
import client.OfflineCrypt
from client.Dialog import Dialog


AUTO_LOG: bool
USERNAME: str
PASSWORD: str
LOGFILE: str = 'applog.log'


def write_log(file_path: str, string: str):
    global AUTO_LOG
    if AUTO_LOG:
        with open(file_path, 'a') as file:
            file.write(str(datetime.datetime.now()) + '$ ' + string+'\n')


def ini_parser(file_path: str):
    """ Function parses settings from file """
    __config = configparser.ConfigParser()
    __config.read(file_path)
    return __config


def session_save(file_path: str, user_tokens, dialogs):
    """ Saves session in file_pathsession.py file """
    file_path = ''.join(filter(lambda key: key != '.', [x for x in file_path]))
    with open(file_path+'session.py', 'w') as file:
        file.write('import datetime\n')
        file.write('user_tokens = {' + ''.join([
            str("'{x}': '{token}',".format(x=x, token=user_tokens[x])) for x in user_tokens]) + '}\n')
        file.write('dialogs = {' +
                   ''.join([str("'{name}': {dialog}, ".format(name=x, dialog=str(vars(dialogs[x]))))
                            for x in dialogs]) + '}')
    return file_path + 'session.py'


def session_load(file_path: str, user_tokens, dialogs):
    """ Loads session from file_pathsession.py file """
    try:
        file_path += 'session'
        file_path = __import__(file_path)
        user_tokens.update(file_path.user_tokens.copy())
        temp_dialogs = file_path.dialogs.copy()
        for dialog in temp_dialogs:
            dialogs.update({dialog: client.Dialog.Dialog.init_from_dict(temp_dialogs[dialog])})
        return "OK"
    except ModuleNotFoundError:
        return "Session module does not found"


def shutdown():
    for task in asyncio.all_tasks():
        if task is not asyncio.tasks.current_task():
            task.cancel()


async def send_message_async(dialog, logfile):
    loop = asyncio.get_event_loop()
    while True:
        message_text = await loop.run_in_executor(None, input, '')
        write_log(logfile, '>>> {}'.format(message_text))
        if message_text == '$EXIT$':
            shutdown()
            break
        else:
            status = dialog.send_message(message_text)
            if status == 'OK':
                write_log(logfile, 'SUCCESS')
            else:
                print('ERROR {}'.format(status))
                shutdown()
                break


async def get_unread_messages(dialog, logfile):
    while True:
        try:
            await asyncio.sleep(4)
            status, messages = dialog.get_unread_messages()
            if status == "OK":
                for message in messages:
                    print("{time} {target_name} :~{text}".format(
                        time=str(message['time']), target_name=message['from'], text=message['text']))
                write_log(logfile, 'SUCCESS')
            else:
                print(status)
                write_log(logfile, "ERROR {status}".format(status=status))
        except asyncio.CancelledError:
            break
        finally:
            status, messages = dialog.get_unread_messages()
            if status == "OK":
                for message in messages:
                    print("{time} {target_name} :~{text}".format(
                        time=str(message['time']), target_name=message['from'], text=message['text']))
                write_log(logfile, 'SUCCESS')
            else:
                print(status)
                write_log(logfile, "ERROR {status}".format(status=status))


def interactive(dialog: Dialog, logfile: str):
    print('----interactive. write $EXIT$ to exit----')

    async def main():
        await asyncio.wait([send_message_async(dialog, logfile),
                            get_unread_messages(dialog, logfile)])

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        loop.close()
    print('----exit----')


def read_command(server: str, username: str, password: str, user_tokens: dict, dialogs: dict, logfile: str):
    """ Command interface """
    input_string = input()
    command = input_string.split()
    write_log(logfile, '>>> ' + input_string)

    if len(command) > 1:
        if command[0] != "Dialog" and command[1] != "sendmessage":
            if not all([x in client.OfflineCrypt.EncryptEN.ALPHABET + [x for x in " -1234567890"]
                        for x in input_string]):
                write_log(logfile, 'ERROR INVALID SYMBOLS')
                print("INVALID SYMBOLS")
                return "INVALID SYMBOLS"
        else:
            if not all([x in client.OfflineCrypt.EncryptEN.ALPHABET + [x for x in " -1234567890"]
                        for x in ' '.join(command[:3])]):
                write_log(logfile, 'ERROR INVALID SYMBOLS')
                print("INVALID SYMBOLS")
                return "INVALID SYMBOLS"

    try:
        if command[0].lower() == "help":
            print("-------------------------------Usage. For more information please read README file-----------------")
            print('-------------------------------UserToken-----------------------------------------------------------')
            print("UserToken create $token_name$                       | Creates new user token")
            print("UserToken add $token_name$ $token$                  | Adds already exist token")
            print("UserToken rename $last_token_name$ $new_token_name$ | Renames token")
            print("UserToken delete $token_name$                       | Deletes token")
            print('-------------------------------Info about deletion time--------------------------------------------')
            print("DeleteInfo                                          | Display time to delete info")
            print('--------------------------------Dialog-------------------------------------------------------------')
            print("Dialog init $user_token$ $dialog_name$              | Initializes new dialog without creation on "
                  "server")
            print('Dialog create $dialog_name$                         | Creates new dialog on server')
            print('Dialog connect $dialog_name$ $dialog_token$         | Connects dialog to server via dialog token')
            print("Dialog setpassword $dialog_name$ $new_password$     | Sets or change offline password in dialog")
            print("Dialog rename $last_name$ $new_name$                | Renames dialog")
            print("Dialog settargetname $dialog_name$ $target_name$    | Sets target name")
            print("Dialog addtoken $dialog_name$ $dialog_token$        | Use it if u already connected to dialog, but"
                  " left")
            print("Dialog autolog $dialog_name$ $bool$                 | If True messages'll auto save after every "
                  "action")
            print("Dialog delete $dialog_name$                         | Clears namespace from used dialog name")
            print("Dialog sendmessage $dialog_name$ $message$          | Sends message on server. All words after \n"
                  "$dialog_name$ will be delivered. For ex: 'Dialog sendmessage mydialog hello world' will deliver \n"
                  "message hello world on server. All symbols allowed beside '~' and '^'")
            print("Dialog getmessages $dialog_name$                    | Displays and logs (if turned up) ALL messages")
            print("Dialog getunreadmessages $dialog_name$              | Displays also logs (if turned up) unread"
                  " messages")
            print("Dialog messages $dialog_name$                       | Displays all messages which you ever"
                  " received\n"
                  "or sent (without request on server)")
            print("Dialog reloadmessages $dialog_name$                 | Reloads all messages in dialog and logs "
                  "their \n"
                  "(if turned up) but doesn't display their.")
            print("Dialog logmessages $dialog_name$                    | Logs messages in file "
                  "$created_time_of_dialog$$dialog_name$.log")
            print("Dialog interactive $dialog_name$                    | Activates interactive mode. "
                  "Please read in README")
            print("--------------------------------Session. Please read in README-------------------------------------")
            print("Session save $file_name$                            | Saves session in python file,\n"
                  "don't specify file extension")
            print("Session load $file_name$                            | Loads session from file")
            print("Session clear                                       | Clears current session. It provides deletion"
                  " \n"
                  "all session info beside logs and settings")
            print("Session fullclear                                   | Provides deletion all info include app log, \n"
                  "all message logs, sessions")
            print('--------------------------------EXIT----------------------------------------------------------------')
            print('exit                                                | Exit')

        elif command[0] == "UserToken":
            # Provides UserToken interface
            if command[1] == "create":
                if len(command) > 2:
                    if command[2] not in user_tokens:
                        temp = client.Server.create_user_token(server=server, username=username, password=password)
                        if temp[0] == "OK":
                            user_tokens.update({command[2]: temp[1]})
                            write_log(logfile, "SUCCESS. New user token:'{token}'".format(token=temp[1]))
                        else:
                            print("ERROR {status}".format(status=temp[0]))
                            write_log(logfile, "ERROR {status}".format(status=temp[0]))
                    else:
                        print('Name already used')
                        write_log(logfile, 'ERROR NAME ALREADY USED')
                else:
                    print('Name must exists Try:(UserToken create $name$)')
                    write_log(logfile, 'ERROR INVALID ARGS')

            elif command[1] == "add":
                if len(command) > 2:
                    if command[2] not in user_tokens:
                        if len(command) > 3:
                            user_tokens.update({command[2]: command[3]})
                            write_log(logfile, 'SUCCESS')
                        else:
                            print('Token is empty Try:(UserToken add $name$ $token$)')
                            write_log(logfile, 'ERROR INVALID ARGS')
                    else:
                        print('Name already used')
                        write_log(logfile, 'ERROR NAME ALREADY USED')
                else:
                    print('Name must exists Try:(UserToken add $name$ $token$)')
                    write_log(logfile, 'ERROR INVALID ARGS')

            elif command[1] == "rename":
                if len(command) > 3:
                    if command[2] in user_tokens:
                        if command[3] not in user_tokens:
                            temp = user_tokens.pop(command[2])
                            user_tokens.update({command[3]: temp})
                            write_log(logfile, 'SUCCESS')
                        else:
                            print('Name already used')
                            write_log(logfile, 'ERROR NAME ALREADY USED')
                    else:
                        print('Invalid last token name')
                        write_log(logfile, 'ERROR INVALID LAST TOKEN NAME')
                else:
                    print("Invalid args Try:(UserToken rename $last_name$ $new_name$)")
                    write_log(logfile, 'ERROR INVALID ARGS')

            elif command[1] == "delete":
                if len(command) > 2:
                    if command[2] in user_tokens:
                        user_tokens.pop(command[2])
                        write_log(logfile, 'SUCCESS')
                    else:
                        print('Invalid token name')
                        write_log(logfile, 'ERROR INVALID TOKEN NAME')
                else:
                    print('Invalid args Try:(UserToken delete $token_name$)')
                    write_log(logfile, 'ERROR INVALID ARGS')
            else:
                print("Unknown command")
                write_log(logfile, "ERROR. Unknown command")

        elif command[0] == "DeleteInfo":
            temp = client.Server.get_info(server)
            if temp[0] == 'OK':
                print(temp[1])
                write_log(logfile, 'SUCCESS')
            else:
                print(temp[0])
                write_log(logfile, 'ERROR {status}'.format(status=temp[0]))

        elif command[0] == "Dialog":
            if command[1] == "init":
                if len(command) > 3:
                    if command[2] in user_tokens:
                        if command[3] not in dialogs:
                            dialog = Dialog(user_token=user_tokens[command[2]], server=server, dialog_name=command[3])
                            dialogs.update({command[3]: dialog})
                            write_log(logfile, "SUCCESS. New dialog was initialized {name}".format(name=command[3]))
                        else:
                            print("Dialog name already exists")
                            write_log(logfile, "ERROR DIALOG NAME ALREADY EXIST")
                    else:
                        print("Invalid UserToken")
                        write_log(logfile, 'ERROR INVALID USERTOKEN')
                else:
                    print("Invalid args Try:(Dialog init $user_token$ $dialog_name$)")
                    write_log(logfile, "ERROR INVALID ARGS")

            elif command[1] == "create":
                if len(command) > 2:
                    if command[2] in dialogs:
                        if dialogs[command[2]].dialog_token is None:
                            status, _ = dialogs[command[2]].create()
                            if status == "OK":
                                print(dialogs[command[2]].dialog_token)
                                write_log(logfile, "SUCCESS. Dialog was created. Dialog token {token}".format(
                                    token=dialogs[command[2]].dialog_token))
                            else:
                                print(status)
                                write_log(logfile, "ERROR {status}".format(status=status))
                        else:
                            print("Error dialog already initialized")
                            write_log(logfile, "ERROR dialog already init")
                    else:
                        print("Dialog doesn't exists")
                        write_log(logfile, "ERROR dialog does not exists")
                else:
                    print("Invalid args Try: (Dialog create $dialog_name$)")
                    write_log(logfile, "ERROR INVALID ARGS")

            elif command[1] == "connect":
                if len(command) > 3:
                    if command[2] in dialogs:
                        status = dialogs[command[2]].accept(command[3])
                        if status == 'OK':
                            write_log(logfile, "SUCCESS Dialog was connected to token {token}".format(token=command[3]))
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print('Invalid dialog name')
                        write_log(logfile, 'ERROR Invalid dialog name')
                else:
                    print("Invalid args Try:(Dialog connect $dialog_name$ $dialog_token$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "setpassword":
                if len(command) > 3:
                    if command[2] in dialogs:
                        status = dialogs[command[2]].set_password(key=command[3])
                        if status == "OK":
                            write_log(logfile, "SUCCESS password sets")
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog setpassword $dialog_name$ $password$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "rename":
                if len(command) > 3:
                    if command[2] in dialogs:
                        if command[3] not in dialogs:
                            status = dialogs[command[2]].set_name(command[3])
                            if status == "OK":
                                dialog = dialogs.pop(command[2])
                                dialogs.update({command[3]: dialog})
                                write_log(logfile, "SUCCESS")
                            else:
                                print(status)
                                write_log(logfile, "ERROR {status}".format(status=status))
                        else:
                            print("New dialog name already exists")
                            write_log(logfile, "ERROR new name already used")
                    else:
                        print("Invalid last dialog name")
                        write_log(logfile, "ERROR Invalid last dialog name")
                else:
                    print("Invalid args Try:(Dialog rename $last_name$ $new_name$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "settargetname":
                if len(command) > 3:
                    if command[2] in dialogs:
                        status = dialogs[command[2]].set_target_name(command[3])
                        if status == "OK":
                            write_log(logfile, "SUCCESS")
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid name")
                else:
                    print("Invalid args Try:(Dialog settargetname $dialog_name$ $target_name$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "addtoken":
                if len(command) > 3:
                    if command[2] in dialogs:
                        status = dialogs[command[2]].set_token(command[3])
                        if status == "OK":
                            write_log(logfile, "SUCCESS")
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Dialog name is incorrect")
                        write_log(logfile, 'ERROR Invalid dialog name')
                else:
                    print("Invalid args Try:(Dialog addtoken $dialog_name$ $dialog_token$")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "autolog":
                if len(command) > 3:
                    if command[2] in dialogs:
                        status: str
                        if command[3].lower() == 'true':
                            status = dialogs[command[2]].set_auto_log(True)
                        else:
                            status = dialogs[command[2]].set_auto_log(False)

                        if status == "OK":
                            write_log(logfile, "SUCCESS")
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog autolog $dialog_name$ $bool$")
                    write_log(logfile, 'ERROR Invalid args')

            elif command[1] == "sendmessage":
                if len(command) > 3:
                    if command[2] in dialogs:
                        message = ' '.join([x for x in command[3:]])
                        status = dialogs[command[2]].send_message(message_text=message)
                        if status == "OK":
                            write_log(logfile, "SUCCESS")
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print('Invalid dialog name')
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog sendmessage $dialog_name$ $message$")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "getmessages":
                if len(command) > 2:
                    if command[2] in dialogs:
                        status, messages = dialogs[command[2]].get_messages()
                        if status == "OK":
                            for message in messages:
                                print("{time} {target_name} :~{text}".format(
                                    time=str(message['time']), target_name=message['from'], text=message['text']))
                            write_log(logfile, 'SUCCESS')
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog getmessages $dialog_name$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "getunreadmessages":
                if len(command) > 2:
                    if command[2] in dialogs:
                        status, messages = dialogs[command[2]].get_unread_messages()
                        if status == "OK":
                            for message in messages:
                                print("{time} {target_name} :~{text}".format(
                                    time=str(message['time']), target_name=message['from'], text=message['text']))
                            write_log(logfile, 'SUCCESS')
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog getunreadmessages $dialog_name$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "logmessages":
                if len(command) > 2:
                    if command[2] in dialogs:
                        status = dialogs[command[2]].log_messages()
                        if status == "OK":
                            write_log(logfile, 'SUCCESS')
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog logmessages $dialog_name$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "reloadmessages":
                if len(command) > 2:
                    if command[2] in dialogs:
                        status = dialogs[command[2]].reload_messages()
                        if status == "OK":
                            write_log(logfile, 'SUCCESS')
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog reload $dialog_name$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == 'messages':
                if len(command) > 2:
                    if command[2] in dialogs:
                        status, messages = dialogs[command[2]].get_without_request_messages()
                        if status == "OK":
                            for message in messages:
                                print("{time} {target_name} :~{text}".format(
                                    time=str(message['time']), target_name=message['from'], text=message['text']))
                            write_log(logfile, 'SUCCESS')
                        else:
                            print(status)
                            write_log(logfile, "ERROR {status}".format(status=status))
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog messages $dialog_name$)")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == 'delete':
                if len(command) > 2:
                    if command[2] in dialogs:
                        dialogs.pop(command[2])
                        write_log(logfile, "SUCCESS")
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog delete $dialog_name$")
                    write_log(logfile, "ERROR Invalid args")

            elif command[1] == "interactive":
                if len(command) > 2:
                    if command[2] in dialogs:
                        interactive(dialog=dialogs[command[2]], logfile=logfile)
                    else:
                        print("Invalid dialog name")
                        write_log(logfile, "ERROR Invalid dialog name")
                else:
                    print("Invalid args Try:(Dialog interactive $dialog_name$)")
                    write_log(logfile, "ERROR Invalid args")
            else:
                print('Unknown command')
                write_log(logfile, "ERROR Unknown command")

        elif command[0] == "Session":
            if command[1] == "save":
                if len(command) > 2:
                    status = session_save(command[2], user_tokens=user_tokens, dialogs=dialogs)
                    if status is not None:
                        print("Session saved in {a}".format(a=status))
                        write_log(logfile, "SUCCESS")
                    else:
                        print(status)
                        write_log(logfile, "ERROR {status}".format(status=status))
                else:
                    print('Invalid args Try:(Session save $file_name$)')
                    write_log(logfile, 'ERROR Invalid args')

            elif command[1] == "clear":
                user_tokens.clear()
                dialogs.clear()
                write_log(logfile, 'SUCCESS Cleared')

            elif command[1] == "load":
                if len(command) > 2:
                    user_tokens.clear()
                    dialogs.clear()
                    status = session_load(command[2], user_tokens=user_tokens, dialogs=dialogs)
                    if status == "OK":
                        print('Loaded: UserTokens: {x}'.format(x=', '.join([token for token in user_tokens])))
                        print('Loaded: Dialogs: {x}'.format(x=', '.join([dialogname for dialogname in dialogs])))
                        write_log(logfile, 'SUCCESS'
                                  + 'Loaded: UserTokens: {x}'.format(x=', '.join([token for token in user_tokens]))
                                  + 'Loaded: Dialogs: {x}, '.format(x=', '.join([dialogname for dialogname in dialogs])))
                    else:
                        print(status)
                        write_log(logfile, "ERROR {status}".format(status=status))
                else:
                    print('Invalid args Try:(Session load $file_name$)')
                    write_log(logfile, 'ERROR Invalid args')

            elif command[1] == "fullclear":
                user_tokens.clear()
                for i in dialogs:
                    try:
                        os.remove(dialogs[i].message_log_calculate)
                    except FileNotFoundError:
                        pass
                dialogs.clear()
                if AUTO_LOG:
                    os.remove(logfile)

                names = os.listdir(os.getcwd())
                for name in names:
                    fullname = os.path.join(os.getcwd(), name)
                    if os.path.isfile(fullname):
                        if 'session.py' in fullname:
                            os.remove(fullname)

            else:
                print("Unknown command")
                write_log(logfile, 'ERROR Unknown command')

        elif command[0] == 'exit':
            print("Are you sure ? Unsaved session will be destroyed. If you want to save it,"
                  " please use Session save command. To exit write 'yes'.")
            if input() == 'yes':
                write_log(logfile, 'EXIT')
                exit()
            write_log(logfile, 'Exit canceled')

        else:
            print("Unknown command. Please write 'help' to see usage page.")
            write_log(logfile, 'ERROR Unknown command')
    except IndexError:
        print("Unknown command. Please write 'help' to see usage page.")
        write_log(logfile, 'ERROR Unknown command')


if __name__ == '__main__':
    config = ini_parser('settings.ini')
    SERVER = config['SERVER']['IP'] + ':' + config['SERVER']['PORT']
    AUTO_LOG = config['APP']['AUTO_LOG'].lower() == "true"
    USERNAME = config['AUTH']['USERNAME']
    PASSWORD = config['AUTH']['PASSWORD']

    if USERNAME == '':
        USERNAME = input('Please enter UserName\n')
    if PASSWORD == '':
        PASSWORD = input('Please enter Password\n')

    if AUTO_LOG:
        LOGFILE = config['APP']['LOGFILE']
    UserTokens = {}
    Dialogs = {}

    while True:
        read_command(server=SERVER, username=USERNAME, password=PASSWORD, user_tokens=UserTokens,
                     dialogs=Dialogs, logfile=LOGFILE)



