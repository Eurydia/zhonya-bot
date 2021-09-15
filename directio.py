from datetime import time

import discord
from discord.ext import commands

from errors import UserCancelledProcess
from questions import ask_title, ask_description, ask_timezone, ask_startup, ask_post_time
from reminder import Reminder

async def reminder_factory(
	bot: commands.Bot, 
	caller: discord.member.Member,
	channel: discord.channel.TextChannel) -> Reminder:   

	try:
		title = await ask_title(bot, caller)
		description = await ask_description(bot, caller)
		local_timezone = await ask_timezone(bot, caller)
		startup = await ask_startup(bot, caller)
		local_post_time = await ask_post_time(bot, caller)

	except (TimeoutError, UserCancelledProcess) as stopping_error:
		raise stopping_error

	local_event_time = time.fromisoformat(startup.strftime('%H:%M'))
	new_task = Reminder(
        title=title, 
        description=description, 
        channel=channel,
        local_event_time=local_event_time,
        local_post_time=local_post_time,
		local_timezone=local_timezone,
		startup=startup)

	return new_task

