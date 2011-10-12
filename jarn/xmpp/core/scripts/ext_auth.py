#!/usr/bin/python

import sys, logging
from struct import pack, unpack


class EjabberdInputError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class EjabberdAuthenticator(object):

    def __init__(self, auth_url):
        self.auth_url = auth_url

    def genereteAnswer(self, bool):
        answer = 0
        if bool:
            answer = 1
        token = pack('>hh', 2, answer)
        return token 

    def ejabberd_out(self, bool):
        token = self.generateAnswer(bool)
        sys.stdout.write(token)
        sys.stdout.flush()

    def ejabberd_in(self):
        try:
            input_length = sys.stdin.read(2)
        except IOError:
            pass
        if len(input_length) is not 2:
            raise EjabberdInputError('Wrong input from ejabberd!')
        (size,) = unpack('>h', input_length)
        return sys.stdin.read(size).split(':')

    def auth(self, username, server, password):
        return False

    def isuser(self, username, server):
        return False

    def setpass(self, username, server, newpassword):
        return False

    def run(self):
        while True:
            try: 
                data = self.ejabberd_in()
            except EjabberdInputError:
                break

            success = False

            if data[0] == "auth":
                success = self.auth(data[1], data[2], data[3])
                self.ejabberd_out(success)

            elif data[0] == "isuser":
                success = self.isuser(data[1], data[2])
                self.ejabberd_out(success)

            elif data[0] == "setpass":
                success = self.setpass(data[1], data[2], data[3])
                self.ejabberd_out(success)

# this is our main-loop. I hate infinite loops.
def run(auth_url, log=None):
    if log is not None:
        sys.stdout = open(log, 'a')
        sys.stderr = open(log, 'a')

    authenticator = EjabberdAuthenticator(auth_url)
    authenticator.run()
