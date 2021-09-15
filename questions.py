from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from datetime import datetime, time

import discord
from discord.ext import commands

from reminder import Reminder
from errors import UserCancelledProcess, UserTimeoutError

def q_embed(
	title: str, 
	description: str, 
	color: discord.colour.Colour = discord.Colour.blurple(),
    footer = 'To exit, simply type \'cancel\'') -> discord.embeds.Embed:
	embed = discord.Embed(
		title=title,
		description=description,
		color=color)
	embed.set_footer(text=footer)
	return embed

def check_message(channel, caller1, caller2):
	return isinstance(channel, discord.channel.DMChannel) and \
		caller1 == caller2

async def ask(bot: commands.Bot, caller: discord.member.Member, timeout = 45, cancellable= True) -> str:
	ans = await bot.wait_for(
		event='message', 
		check=lambda m: check_message(m.channel, caller, m.author),
		timeout=timeout)
	ans_content = ans.content
	if ans_content.lower() == 'cancel' and cancellable:
		raise UserCancelledProcess       
	return ans_content

async def ask_title(bot: commands.Bot, caller: discord.member.Member) -> str:
	await caller.send(embed=q_embed(
		title='Enter the event title',
		description='Enter your event title. Up to 200 characters are permitted.')
		)
	while True:
		try:
			title = await ask(bot, caller)
		except (UserTimeoutError, UserCancelledProcess) as stopping_error:
			raise stopping_error

		if len(title) <= 200:
			return title
		await caller.send(content='Invalid entry. Characters exceed length. Please try again:')

async def ask_description(bot: commands.Bot, caller: discord.member.Member) -> str:
	await caller.send(embed=q_embed(
		title='Enter the event description',
		description='Type `None` for no description. Up to 1600 characters are permitted.')
		)
	while True:
		try:
			description = await ask(bot, caller, 90)
		except (UserTimeoutError, UserCancelledProcess) as stopping_error:
			raise stopping_error

		if len(description) <= 1600:
			if description.lower() == 'none':
				description = ''
			return description   
		await caller.send(content='Invalid entry. Characters exceed length. Please try again:')
	
async def ask_timezone(bot: commands.Bot, caller: discord.member.Member) -> ZoneInfo:
	#Ask for timezone
	await caller.send(embed=q_embed(
		title='Enter your local time zone',
		description='Please enter your time zone in the IANA format (Case sensitive).\n\
			Check you timezone [HERE](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).\n\
				>>> Japan\n\
				Asia/Seoul\n\
				America/Indiana/Tell_City'))
	while True:
		try:
			tzname = await ask(bot, caller, 120)
		except (UserTimeoutError, UserCancelledProcess) as stopping_error:
			raise stopping_error
		
		try:
			local_timezone = ZoneInfo(tzname)
		except ZoneInfoNotFoundError:
			await caller.send(content='Invalid entry. Unknown timezone. Please try again:')
		else:
			return local_timezone

async def ask_startup(bot: commands.Bot, caller: discord.member.Member) -> datetime:
	await caller.send(embed=q_embed(
		title='When should the event start?',
		description='Please enter in one of the format shown below.\n\
			>>> YYYY-MM-DD HH:mm')
			)
	while True:
		try:
			start_time = await ask(bot, caller, 90)
		except (UserTimeoutError, UserCancelledProcess) as stopping_error:
			raise stopping_error
		
		try:
			startup = datetime.fromisoformat(start_time)
		except ValueError:
			await caller.send(content='Invalid entry. Unable to read format. Please try again:')
		else:
			return startup

async def ask_post_time(bot: commands.Bot, caller: discord.member.Member) -> time:
	await caller.send(embed=q_embed(
		title='When should the event be posted?',
		description='Please enter in one of the format shown below.\n\
			>>> HH:MM')
			)
	while True:
		try:
			post_time = await ask(bot, caller, 90)
		except (UserTimeoutError, UserCancelledProcess) as stopping_error:
			raise stopping_error
		
		try:
			local_post_time = time.fromisoformat(post_time)
		except ValueError:
			await caller.send(content='Invalid entry. Unable to read format. Please try again:')
		else:
			return local_post_time

async def ask_field(bot: commands.Bot, caller: discord.member.Member, reminder: Reminder) -> int: 
    await caller.send(embed=q_embed(
		title='What would you like to modify?',
		description=f'**1** - Title\n`{reminder.title}`\n\
        **2** - Description\n`{reminder.description}`\n\
        **3** - Start Time\n`{reminder.startup}`\n\
        **4** - Timezone\n`{reminder.local_timezone}`\n\
        **5** - Post Time\n`{reminder.local_post_time}'))

    while True:
        try:
            field_indx = await ask(bot, caller, 90)
        except (UserTimeoutError, UserCancelledProcess) as stopping_error:
            raise stopping_error
        
        try:
            indx = int(field_indx)
            if indx > 5 or indx < 1:
                raise ValueError
        except ValueError:
            await caller.send(content='Invalid entry. Please enter a valid number. Please try again:')
        else:
            return indx

async def ask_exit_mod(bot: commands.Bot, caller: discord.member.Member) -> int:
    await caller.send(embed=q_embed(
		title='Would you like to keep editing?',
		description='**1** No, I\'m all done.\n**2** Yes, keep editing',
        footer=''))

    while True:
        try:
            indx = await ask(bot, caller, 90, False)
        except UserTimeoutError:
            raise UserTimeoutError
        
        try:
            indx = int(indx)
            if indx > 2 or indx < 1:
                raise ValueError
        except ValueError:
            await caller.send(content='Invalid entry. Please enter a valid number. Please try again:')
        else:
            return indx
