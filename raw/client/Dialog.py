# Dialog.py
""" Provides access to dialog.
Every method must returns status and only then values. If success status must be 'OK' else string of Error message.
Get messages methods interface:
messages = [{'from': 'me or target_name if not empty else word "target"', 'time': datetime.datetime, 'text': text},
            {...}, ...]"""
import datetime
import client.OfflineCrypt
import os
import json
import requests
import asyncio


def request_to_dict(method='get', key=None, *args, **kwargs):
    method = method.upper()
    if method == 'GET':
        response = requests.get(*args, **kwargs)
    elif method == 'POST':
        response = requests.post(*args, **kwargs)
    else:
        return 'unknown method', None

    if response.status_code == 200:
        dictionary = json.loads(response.content)
        try:
            return dictionary['Status'], dictionary[key]
        except KeyError:
            return dictionary['Status'], None

    return response.status_code, None


class Dialog:
    def __init__(self, user_token: str, server: str, dialog_token=None, messages=[], dialog_name=None,
                 target_name=None, auto_log=False, key=""):
        self.user_token = user_token  # User token
        self.server = server  # Server
        self.dialog_token = dialog_token  # Dialog token if exists at start
        self.messages = messages  # Array that saves messages
        self.created_time = datetime.datetime.now()  # Saves created time
        self.dialog_name = dialog_name  # Pins dialog name
        self.target_name = target_name  # Pins target name
        self.auto_log = auto_log  # If True message will saves in file automatic
        self.key = key  # Offline key to decrypt messages
        self.messages_log = str(self.created_time.date()) + str(self.created_time.hour) + \
                            str(self.created_time.minute) + str(self.created_time.second)

    def __mod(self, **kwarg):
        """ Mod settings """
        attr = kwarg.__iter__().__next__()
        if hasattr(self, attr):
            setattr(self, attr, kwarg[attr])
            return "OK"
        return "Not founded"

    def create(self):
        """ Sends POST request to server to create new dialog and returns DialogToken """
        self.data_clear()

        url = '{server}/api/newdialog'.format(server=self.server) if 'http://' in self.server else \
            'http://{server}/api/newdialog'.format(server=self.server)
        status, data = request_to_dict('post', url=url, key='DialogToken', data={'UserToken': self.user_token})

        if status == "OK":
            self.dialog_token = data
            return status, data
        return status, ""

    def data_clear(self):
        """ Removes all data about dialog """
        self.messages.clear()
        try:
            os.remove(self.message_log_calculate())
        except FileNotFoundError:
            pass

    def accept(self, dialog_token):
        """ Sends POST request to server to accept dialog """
        self.data_clear()

        url = '{server}/api/acceptdialog'.format(server=self.server) if 'http://' in self.server else \
            'http://{server}/api/acceptdialog'.format(server=self.server)
        status, _ = request_to_dict('post', url=url, data={'UserToken': self.user_token, 'DialogToken': dialog_token})

        if status == "OK":
            self.dialog_token = dialog_token
        return status

    def set_name(self, dialog_name):
        """ Pin name to dialog """
        return self.__mod(dialog_name=dialog_name)

    def set_target_name(self, target_name):
        """ Pin target name to dialog """
        return self.__mod(target_name=target_name)

    def set_password(self, key):
        """ Sets new password to dialog """
        if all([x in client.OfflineCrypt.EncryptEN.ALPHABET for x in key]):
            return self.__mod(key=key)

    def set_token(self, dialog_token):
        """ Sets dialog token """
        return self.__mod(dialog_token=dialog_token)

    def set_auto_log(self, value):
        """ Sets auto log variable """
        return self.__mod(auto_log=value)

    def send_message(self, message_text):
        """ Sends POST request to server to send message """
        url = '{server}/api/sendmessage'.format(server=self.server) if 'http://' in self.server else \
            'http://{server}/api/sendmessage'.format(server=self.server)
        status, _ = request_to_dict('post', url=url, data={
            'UserToken': self.user_token, 'DialogToken': self.dialog_token, 'MessageText':
                client.OfflineCrypt.EncryptEN.encrypt(key=self.key, message=message_text)})

        return status

    def __get_messages_only_request_and_minimal_treatment(self):
        """ Raw response from get messages request. Sends GET request to server to get all messages """

        url = '{server}/api/getmessages'.format(server=self.server) if 'http://' in self.server else \
            'http://{server}/api/getmessages'.format(server=self.server)

        status, messages = request_to_dict('get', key='Messages', url=url, params={
            'UserToken': self.user_token, 'DialogToken': self.dialog_token})

        if status == "OK":
            msg = []
            for message in messages:
                time = message['Time']
                from_who = 'me' if message['FromMe'] is True\
                    else 'target' if self.target_name is None else self.target_name
                text = client.OfflineCrypt.EncryptEN.decrypt(message=message['Text'], key=self.key)
                message_temp = {'time': time, 'from': from_who, 'text': text}
                msg.append(message_temp)

            return status, msg
        return status, []

    def get_messages(self):
        """ Wrapper over __get_messages_..._treatment """

        status, messages = self.__get_messages_only_request_and_minimal_treatment()
        message_dates = [msg['time'] for msg in self.messages]
        if status == 'OK':
            for message in messages:
                if message['time'] not in message_dates:
                    self.messages.append(message)
                    if self.auto_log:
                        self.write_log_message(message)

        return status, self.messages

    def get_unread_messages(self):
        """ This function is like on get_messages func. But unlike it, it provides sorting return """

        status, messages = self.__get_messages_only_request_and_minimal_treatment()
        message_dates = [message['time'] for message in self.messages]
        msg = []
        if status == 'OK':
            for message in messages:
                if message['time'] not in message_dates:
                    self.messages.append(message)
                    if self.auto_log:
                        self.write_log_message(message)
                    if message['from'] != 'me':
                        msg.append(message)

        return status, msg

    def reload_messages(self):
        """ Reloads all messages. It needs then you set wrong password or after target renaming """

        status, messages = self.__get_messages_only_request_and_minimal_treatment()

        if status == "OK":
            self.messages.clear()
            try:
                os.remove(self.message_log_calculate())
            except FileNotFoundError:
                pass
            for message in messages:
                self.messages.append(message)
                if self.auto_log:
                    self.write_log_message(message)

        return status

    def log_messages(self):
        """ Logs all your messages in file: created_timedialog_name.log created_time is str(datetime) without 'space'
         between parts of datetime """

        status, messages = self.__get_messages_only_request_and_minimal_treatment()

        message_dates = [msg['time'] for msg in self.messages]

        try:
            os.remove(self.message_log_calculate())
        except FileNotFoundError:
            pass

        if status == 'OK':
            for message in messages:
                if message['time'] not in message_dates:
                    self.messages.append(message)

                self.write_log_message(message)

        return status

    def get_without_request_messages(self):
        """ Method does not need in default but here you can catch messages if you need"""
        return 'OK', self.messages

    def write_log_message(self, message):
        """ Writes message in log file with required format """
        self.message_log_calculate()
        with open(self.messages_log, 'a', encoding='UTF-8') as file:
            file.write('{time} {from_}~$ {text}\n'.format(time=message['time'],
                                                          from_=message['from'], text=message['text']))

    def message_log_calculate(self):
        """ Calculate name of log file """
        self.messages_log = str(self.created_time.date()) + str(self.created_time.hour) + \
                            str(self.created_time.minute) + str(self.created_time.second)

        if self.dialog_name is not None:
            self.messages_log += self.dialog_name

        self.messages_log += '.log'

        return self.messages_log

    @staticmethod
    def init_from_dict(dialog: dict):
        """ Init dialog from dict with self parameters """
        # Parsing with hand self control is better than use exec or uncontrollable __mod method

        new_dialog = Dialog(
            user_token=dialog['user_token'], server=dialog['server'], dialog_token=dialog['dialog_token'],
            messages=dialog['messages'], dialog_name=dialog['dialog_name'], target_name=dialog['target_name'],
            auto_log=dialog['auto_log'], key=dialog['key'])
        new_dialog.__mod(created_time=dialog['created_time'])
        new_dialog.message_log_calculate()

        return new_dialog
