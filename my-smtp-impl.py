from aiosmtpd.controller import Controller
from aiosmtpd.smtp import SMTP as Server, syntax
from aiosmtpd.handlers import Sink
import datetime


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

    # @syntax('HELP [command]')
    # async def smtp_HELP(self, arg: str) -> None:
    #     await self.push('help-called')

    @syntax('AUTH [command]')
    async def smtp_AUTH(self, arg: str):
        log(arg)
        await self.push('auth-starting...')


class MyController(Controller):

    def factory(self):
        return MyServer(self.handler)


log('Staring SMTP server...')

controller = MyController(Sink())
controller.start()
log(controller.hostname + ' ' + str(controller.port))
input("Press enter to exit;\n")
log('Stopping SMTP server...')
controller.stop()
