import discord
	
async def is_channel(guild: discord.guild.Guild) -> int:
	for channel in guild.channels:
		if isinstance(channel, discord.channel.TextChannel) and \
			channel.name == 'zhonya-event-channel':
			return channel.id
	return 0

async def create_channel(
	guild: discord.guild.Guild,
	category: discord.CategoryChannel) -> int:

	channel: discord.channel.TextChannel = await guild.create_text_channel(
		'zhonya-event-channel',
		category=category)
		
	await set_channel_permission(channel)

	return channel.id
	
async def set_channel_permission(
	guild: discord.guild.Guild, 
	channel: discord.channel.TextChannel) -> None:

	await channel.set_permissions(
		guild.default_role, 
		read_messages=True, 
		send_messages=False, 
		add_reactions=True)

	await channel.set_permissions(
		guild.get_member_named('Zhonya bot#2389'), 
		view_channel=True,
		embed_links=True,
		read_messages=True, 
		send_messages=True,
		manage_messages=True,
		read_message_history=True, 
		add_reactions=True,
		use_external_emojis=True)

