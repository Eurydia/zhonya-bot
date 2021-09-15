from asyncio import create_task, sleep
from datetime import datetime, time, timedelta
from typing import Union
from backports.zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

def local_now(tz: ZoneInfo) -> datetime:
    return datetime.now(tz).replace(microsecond=0)

def date_component(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d')

def time_component(dt: datetime) -> str:
    return dt.isoformat().split('T')[1]

class Reminder(commands.Cog):
    def __init__(self, 
    title: str, 
    description: str,
    channel: discord.channel.TextChannel,
    local_event_time: time,
    local_post_time: time,
    local_timezone: ZoneInfo,
    startup: Union[datetime, None]) -> None:

        self.title = title
        self.description = description
        self.channel = channel

        self.local_event_time = local_event_time.replace(tzinfo=local_timezone)
        self.local_post_time = local_post_time.replace(tzinfo=local_timezone)
        self.local_timezone = local_timezone
        self.startup = startup.replace(tzinfo=local_timezone)

    async def send_embed(self, target) -> discord.embeds.Embed:
        embed: discord.embeds.Embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=discord.Color.blurple()
        )
        now_date: str = date_component(local_now(self.local_timezone))
        now_time: str = self.local_event_time.isoformat()
        now: datetime = datetime.fromisoformat(f'{now_date} {now_time}').replace(tzinfo=self.local_timezone)
        time_stamp = int(now.timestamp())

        embed.add_field(
            name='Time',
            value=f'<t:{time_stamp}:F>\n🕐<t:{time_stamp}:R>')
        await target.send(embed=embed)

    @tasks.loop(hours=24)
    async def post(self):       
        await self.send_embed(self.channel)

    @post.before_loop
    async def align_post(self):
        now: datetime = local_now(self.local_timezone)

        post_time: datetime = datetime.fromisoformat(
            f'{date_component(now)} {self.local_event_time.isoformat()}'
            )
        post_time = post_time.replace(tzinfo=self.local_timezone)

        delta: timedelta = post_time - now
        delta_total = int(delta.total_seconds())
        
        if delta_total < 0:
            delta_total += 24 * 60 * 60
        await sleep(delta_total)

    async def start(self):
        if self.startup:
            now = local_now(self.local_timezone)
            delta = self.startup - now 
            delta_total = int(delta.total_seconds())
            if delta_total > 0:
                await sleep(delta_total)
            else:
                self.startup = None
        self.post.start()

    def stop(self):
        self.event.cancel()

    def edit_title(self, title: str):
        self.title = title
    
    def edit_description(self, description: str):
        self.description = description
    
    def edit_local_event_time(self, local_event_time: time):
        self.local_event_time = local_event_time

    def edit_local_post_time(self, local_post_time: time):
        self.local_post_time = local_post_time
    
    def edit_local_timezone(self, local_timezone: ZoneInfo):
        self.local_timezone = local_timezone
    
    def edit_startup(self, startup: datetime):
        self.stop()
        self.startup = startup
        self.local_event_time = time_component(startup).replace(self.local_timezone)
        create_task(self.start())
