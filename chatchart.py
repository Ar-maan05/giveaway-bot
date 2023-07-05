import asyncio
import discord
import heapq
from io import BytesIO
from typing import List, Optional, Tuple, Union
from discord.ext import commands

import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
plt.switch_backend("agg")


class Chatchart(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def calculate_member_perc(history: List[discord.Message]) -> dict:
        """Calculate the member count from the message history"""
        msg_data = {"total_count": 0, "users": {}}
        for msg in history:
            # Name formatting
            if len(msg.author.name) >= 20:
                short_name = "{}...".format(msg.author.name[:20]).replace("$", "\\$")
            else:
                short_name = msg.author.name.replace("$", "\\$").replace("_", "\\_ ").replace("*", "\\*")
            whole_name = "{}#{}".format(short_name, msg.author.discriminator)
            if msg.author.bot:
                pass
            elif whole_name in msg_data["users"]:
                msg_data["users"][whole_name]["msgcount"] += 1
                msg_data["total_count"] += 1
            else:
                msg_data["users"][whole_name] = {}
                msg_data["users"][whole_name]["msgcount"] = 1
                msg_data["total_count"] += 1
        return msg_data

    @staticmethod
    def calculate_top(msg_data: dict) -> Tuple[list, int]:
        """Calculate the top 20 from the message data package"""
        for usr in msg_data["users"]:
            pd = float(msg_data["users"][usr]["msgcount"]) / float(msg_data["total_count"])
            msg_data["users"][usr]["percent"] = pd * 100
        top_twenty = heapq.nlargest(
            20,
            [
                (x, msg_data["users"][x][y])
                for x in msg_data["users"]
                for y in msg_data["users"][x]
                if (y == "percent" and msg_data["users"][x][y] > 0)
            ],
            key=lambda x: x[1],
        )
        others = 100 - sum(x[1] for x in top_twenty)
        return top_twenty, others

    @staticmethod
    async def create_chart(top, others, channel: discord.TextChannel):
        plt.clf()
        sizes = [x[1] for x in top]
        labels = ["{} {:g}%".format(x[0], round(x[1], 1)) for x in top]
        if len(top) >= 20:
            sizes = sizes + [others]
            labels = labels + ["Others {:g}%".format(round(others, 1))]
        if len(channel.name) >= 19:
          channel_name = "#{}...".format(channel.name[:19])
        else:
            channel_name = channel.name
        title = plt.title("Chat Chart for the channel.")
        title.set_va("top")
        title.set_ha("center")
        plt.gca().axis("equal")
        colors = [
            "r",
            "darkorange",
            "gold",
            "y",
            "olivedrab",
            "green",
            "darkcyan",
            "mediumblue",
            "darkblue",
            "blueviolet",
            "indigo",
            "orchid",
            "mediumvioletred",
            "crimson",
            "chocolate",
            "yellow",
            "limegreen",
            "forestgreen",
            "dodgerblue",
            "slateblue",
            "gray",
        ]
        pie = plt.pie(sizes, colors=colors, startangle=0)
        plt.legend(
            pie[0],
            labels,
            bbox_to_anchor=(0.7, 0.5),
            loc="center",
            fontsize=10,
            bbox_transform=plt.gcf().transFigure,
            facecolor="#ffffff",
        )
        plt.subplots_adjust(left=0.0, bottom=0.1, right=0.45)
        image_object = BytesIO()
        plt.savefig(image_object, format="PNG", facecolor="#36393E")
        image_object.seek(0)
        return image_object

    async def fetch_channel_history(
        self,
        channel: discord.TextChannel,
        animation_message: discord.Message,
        messages: int
    ) -> List[discord.Message]:
        """Fetch the history of a channel while displaying an status message with it"""
        animation_message_deleted = False
        history = []
        history_counter = 0
        async for msg in channel.history(limit=messages):
            history.append(msg)
            history_counter += 1
            if history_counter % 250 == 0:
                new_embed = discord.Embed(
                    title=f"Fetching messages from the Discord API...",
                    description=f"This may take a while.\n{history_counter}/{messages} messages fetched",
                    colour=discord.Color.dark_blue(),
                )
                if channel.permissions_for(channel.guild.me).send_messages:
                    await channel.trigger_typing()
                if animation_message_deleted is False:
                    try:
                        await animation_message.edit(embed=new_embed)
                    except discord.NotFound:
                        animation_message_deleted = True
        return history

    @commands.guild_only()
    @commands.slash_command(description = "Sends a pie chart of the last 5000 messages of the specified channel.")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.bot_has_permissions(attach_files=True)
    async def chatchart(self,
                        ctx,
                        channel: discord.Option(
                            discord.TextChannel, 
                            "The text channel for which the chatchart has to be made.", 
                            required = False
                        ), 
                        messages: discord.Option(
                            int, 
                            "The number of messages to be searched (default: 5000)", 
                            required = False
                        )
        ):

        if channel is None:
            channel = ctx.channel

        if messages is None:
            messages = 5000

        backup_ctx_channel = ctx.channel

        await ctx.respond("**Calculating...**")


        embed = discord.Embed(
            title=f"Fetching messages from the Discord API...",
            description="This may take a while.",
            colour=discord.Color.dark_blue()
        )
        loading_message = await ctx.send(embed=embed)
        try:
            history = await self.fetch_channel_history(channel, loading_message, messages)
        except discord.errors.Forbidden:
            try:
                await loading_message.delete()
            except discord.NotFound:
                pass
            return await backup_ctx_channel.send("No permissions to read that channel.")

        msg_data = self.calculate_member_perc(history)
        # If no members are found.
        if len(msg_data["users"]) == 0:
            try:
                await loading_message.delete()
            except discord.NotFound:
                pass
            return await ctx.send(f"Only bots have sent messages in {channel.mention} or I can't read message history.")

        top_twenty, others = self.calculate_top(msg_data)
        chart = await self.create_chart(top_twenty, others, channel)

        try:
            await loading_message.delete()
        except discord.NotFound:
            pass
        await backup_ctx_channel.send(file=discord.File(chart, "chart.png"))

def setup(bot):
  bot.add_cog(Chatchart(bot))
