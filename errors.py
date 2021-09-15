from asyncio import TimeoutError

class ZhonyaErrors(Exception):
	def __init__(self, message: str) -> None:
		self.message = message
	
	async def report_error(self, channel):
		await channel.send(content=self.message)

class OwnershipError(ZhonyaErrors):
	def __init__(self) -> None:
		super().__init__('Only the owner have access to this bot.')

class UserCancelledProcess(ZhonyaErrors):
	def __init__(self) -> None:
		super().__init__('Process cancelled.')

class UserInvokedCommandInDM(ZhonyaErrors):
	def __init__(self) -> None:
		super().__init__('You can\'t use that command in a private message.')
		
class UserAlreadyInSession(ZhonyaErrors):
	def __init__(self) -> None:
		super().__init__('You are already creating an event. Check your DMs with me!')

class UserTimeoutError(TimeoutError):
	def __init__(self, **kwarg):
		super().__init__(**kwarg)
		self.msg = 'I\'m not sure where you went. We can try this again later.'
	
	async def report_error(self, channel):
		await channel.send(content=self.msg)
