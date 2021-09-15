from os import getenv

from discord.ext import commands

from zhonya import Zhonya

# #TODO
# #- Database integration
# #- When calling task creator function also add the task to a database
# #- when starting a new session get pull previous tasks from database

def main() -> None:	
	cmd_prefix = '.'
	bot = commands.Bot(command_prefix=cmd_prefix)

	zhonya = Zhonya(int(getenv("MY_ID")), bot)
	bot.add_cog(zhonya)

	bot.run(getenv("TOKEN"))
if __name__ == '__main__':
	main()

