from typing import List
from asyncio import create_task

import discord
from discord.ext import commands

from directio import reminder_factory
from questions import ask_title, ask_description, ask_timezone, ask_field, ask_startup, ask_post_time, ask_exit_mod
from channel import is_channel, create_channel, set_channel_permission
from reminder import Reminder
from errors import UserCancelledProcess, UserInvokedCommandInDM, OwnershipError, UserAlreadyInSession, UserTimeoutError


class Zhonya(commands.Cog):
    def __init__(self, 
    owner_id: int,
    bot: commands.Bot) -> None:
        self._event_pool: List[Reminder] = []
        self._owner_id = owner_id
        self._in_session = False
        self._channel_id = 0

        self.bot = bot
    
    def prevent_dm_call(
        self, 
        channel: discord.channel,
        caller_id: int):
        if isinstance(channel, discord.channel.DMChannel):
            raise UserInvokedCommandInDM

        if caller_id != self._owner_id:
            raise OwnershipError

        if self._in_session:
            raise UserAlreadyInSession

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.bot.change_presence(
            status=discord.Status.online, 
            activity=discord.Game(name='with the vibe.'))
        print(f'Bot ready USER: {self.bot.user}')

    @commands.command(name='edit')
    async def _edit(self, ctx: commands.Context, indx: int):
        channel = ctx.channel
        caller = ctx.author
        try:
            self.prevent_dm_call(
                channel,
                caller.id
            )
        except (UserAlreadyInSession, OwnershipError, UserInvokedCommandInDM) as e:
            await e.report_error(ctx.channel)
            return
        else:
            self._in_session = True

        try:
            in_focus = self._event_pool[indx]
        except IndexError:
            await channel.send(content='Index out of range')
            self._in_session = False
            return

        while True:
            try:
                field = await ask_field(self.bot, ctx.author, in_focus)
                if field == 1:
                    new_title = await ask_title(self.bot, caller)
                    in_focus.edit_title(new_title)

                elif field == 2:
                    new_description = await ask_description(self.bot, caller)
                    in_focus.edit_description(new_description)

                elif field == 3:
                    new_startup = await ask_startup(self.bot, caller)
                    in_focus.edit_startup(new_startup)
                
                elif field == 4:
                    new_tz = await ask_timezone(self.bot, caller)
                    in_focus.edit_timezone(new_tz)

                else:
                    new_post_time = await ask_post_time(self.bot, caller)
                    in_focus.edit_local_post_time(new_post_time)
                
                confirm_mod = await ask_exit_mod(self.bot, caller)
                if confirm_mod == 1:
                    self._in_session = False
                    return
            except (TimeoutError, UserCancelledProcess) as stopping_error:
                await stopping_error.report_error(channel)
                self._in_session = False
                return
    
    @commands.command(name='del')
    async def _list(self, ctx: commands.Context, indx: int):
        channel = ctx.channel
        try:
            in_focus = self._event_pool[indx]
        except IndexError:
            await channel.send(contet='Index out of range')
            return
        self._event_pool.pop(indx)
        in_focus.stop()

    @commands.command(name='list')
    async def _list(self, ctx: commands.Context):
        caller = ctx.author
        if not self._event_pool:
            await caller.send(content='No event in event pool.')
            return
        await caller.send(content='Here are all of your event(s).')
        for i, reminder in enumerate(self._event_pool):
            await caller.send(content=f'**#{i}**')
            await reminder.send_embed(caller)

    @commands.command(name='event')
    async def _event(self, ctx: commands.Context):
        caller: discord.member.Member = ctx.author
        channel = ctx.channel

        try:
            self.prevent_dm_call(
                channel,
                caller.id
            )
        except (UserAlreadyInSession, OwnershipError, UserInvokedCommandInDM) as e:
            await e.report_error(channel)
            return
        else:
            self._in_session = True

        try:
            new_task: Reminder = await reminder_factory(self.bot, caller, channel)
        except (UserTimeoutError, UserCancelledProcess) as stopping_error:
            await stopping_error.report_error(channel)
            self._in_session = False
            return
        else:
            self._in_session = False
            await new_task.send_embed(channel)
            await caller.send(content='New event created.')

        create_task(new_task.start())
        self._event_pool.append(new_task)

    @commands.command(name='channel')
    async def _channel(self, ctx: commands.Context):
        guild: discord.guild.Guild = ctx.guild
        
        existing_channel = is_channel(guild)
        if not existing_channel:
            self._channel_id = create_channel(guild, ctx.channel.category)
            return
        
        self._channel_id = existing_channel
        set_channel_permission(guild, guild.get_channel(self._channel_id))
    
