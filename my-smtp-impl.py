from email.message import EmailMessage

from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as Server, syntax, Session
from aiosmtpd.handlers import Sink, AsyncMessage
import datetime
import asyncio
import base64
from email.utils import parsedate_to_datetime
import json
import traceback
import my_smtp_relay_handler

# Define your user credentials (in a real application, use a secure storage)
USER_CREDENTIALS = {
    "adam": "adam"  # username: password
}

def authenticate(username, password):
    return USER_CREDENTIALS.get(username) == password


def log(values: str):
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(time_now + ' | ' + values)




class MyServer(Server):
    def __init__(self, handler):
        super().__init__(handler, auth_required=True, hostname='adam-pc')

    @syntax('PING [Ignored]')
    async def smtp_PING(self, arg):
        log('Request for ping')
        await self.push('259 Pong')

    # @syntax('Help [command]')
    # async def smtp_HELP(self, arg):
    #     log('Request for help')
    #     await super().smtp_HELP(self)
    #     # await self.push('help running...')


    @syntax('AUTH [command]')
    async def smtp_AUTH(self, arg: str):
        log(arg)

        if arg.startswith('PLAIN '):
            try:
                _, username, password = base64.b64decode(arg[6:]).decode().split('\x00')
                log('Username: ' + username + ' Password: ' + password)
                if authenticate(username, password):
                    user_session = Session(self.loop)
                    user_session.auth_data = (username, password)
                    user_session.authenticated = True
                    user_session.extended_smtp = True
                    self.session.auth = user_session

                    self.session.authenticated = True
                    self.session.auth_data = (username, password)
                    await self.push('235 Authentication successful')
                else:
                    await self.push('535 Authentication failed')
            except Exception as e:
                log(str(e))
                await self.push('500 Internal server error')
        else:
            await self.push('504 Unrecognized authentication type')



class MyController(Controller):
    def factory(self):
        return MyServer(self.handler)


log('Starting SMTP server...')

controller = MyController(my_smtp_relay_handler.RelayHandler())
controller.hostname = 'localhost'
controller.start()

log(controller.hostname + ' ' + str(controller.port))
input("Press enter to exit;\n")
log('Stopping SMTP server...')
controller.stop()
