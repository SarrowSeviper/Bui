import random
import discord
import json
import requests
import io
import secrets

from io import BytesIO
from discord.ext import commands
from utils import lists, permissions, http, default
from utils.lists import *


class Fun_Commands:
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command(aliases=['8ball'])
    async def eightball(self, ctx, *, question: commands.clean_content):
        """ Consult 8ball to receive an answer """
        answer = random.choice(lists.ballresponse)
        await ctx.send(f"🎱 **Question:** {question}\n**Answer:** {answer}")

    async def randomimageapi(self, ctx, url, endpoint):
        try:
            r = await http.get(url, res_method="json", no_cache=True)
        except json.JSONDecodeError:
            return await ctx.send("Couldn't find anything from the API")

        embed = discord.Embed(colour=0x00ddff)
        embed.set_image(url=r[endpoint])
        await ctx.send(embed=embed)

    async def textapi(self, ctx, url, endpoint):
        try:
            r = await http.get(url, res_method="json", no_cache=True)
        except json.JSONDecodeError:
            return await ctx.send("Couldn't find anything from the API")

        await ctx.send(f"{r[endpoint]}")

    async def factapi(self, ctx, url, endpoint):
        try:
            r = await http.get(url, res_method="json", no_cache=True)
        except json.JSONDecodeError:
            return await ctx.send("Couldn't find anything from the API")

        await ctx.send(f'**Did you know?** 🤔\n\n{r[endpoint]}')


    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def cat(self, ctx):
        """ Posts a random cat """
        await self.randomimageapi(ctx, 'https://nekos.life/api/v2/img/meow', 'url')

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def dog(self, ctx):
        """ Posts a random dog """
        await self.randomimageapi(ctx, 'https://random.dog/woof.json', 'url')

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def neko(self, ctx):
        """ Posts a random neko """
        await self.randomimageapi(ctx, 'https://nekos.life/api/v2/img/neko', 'url')

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def duck(self, ctx):
        """ Posts a random duck """
        await self.randomimageapi(ctx, 'https://random-d.uk/api/v1/random', 'url')

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def fox(self, ctx):
        """ Posts a random fox girl """
        await self.randomimageapi(ctx, 'https://nekos.life/api/v2/img/fox_girl', 'url')

    @commands.command(aliases=['flip', 'coin'])
    async def coinflip(self, ctx):
        """ Coinflip! """
        coinsides = ['Heads', 'Tails']
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coinsides)}**!")

    @commands.command()
    async def reverse(self, ctx, *, text: str):
        """ !poow ,ffuts esreveR
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command()
    async def rate(self, ctx, *, thing: commands.clean_content):
        """ Rates what you desire """
        numbers = random.randint(0, 100)
        decimals = random.randint(0, 9)

        if numbers == 100:
            decimals = 0

        await ctx.send(f"I'd rate {thing} a **{numbers}.{decimals} / 100**")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def urban(self, ctx, *, search: str):
        """ Find the 'best' definition to your words """
        if not permissions.can_embed(ctx):
            return await ctx.send("I cannot send embeds here ;-;")

        url = await http.get(f'http://api.urbandictionary.com/v0/define?term={search}', res_method="json")

        if url is None:
            return await ctx.send("I think the API broke...")

        count = len(url['list'])
        if count == 0:
            return await ctx.send("Couldn't find your search in the dictionary...")
        result = url['list'][random.randint(0, count - 1)]

        definition = result['definition']
        if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(' ', 1)[0]
                definition += '...'

        embed = discord.Embed(colour=0xC29FAF, description=f"**{result['word']}**\n*by: {result['author']}*")
        embed.add_field(name='Definition', value=definition, inline=False)
        embed.add_field(name='Example', value=result['example'], inline=False)
        embed.set_footer(text=f"👍 {result['thumbs_up']} | 👎 {result['thumbs_down']}")

        try:
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("I found something, but have no access to post it... [Embed permissions]")

    @commands.command(aliases=['howhot', 'hot'])
    async def hotcalc(self, ctx, user: discord.Member = None):
        """ Returns a random percent for how hot is a discord user """
        if user is None:
            user = ctx.author

        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        emoji = "💔"
        if hot > 25:
            emoji = "❤"
        if hot > 50:
            emoji = "💖"
        if hot > 75:
            emoji = "💞"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command()
    async def yell(self, ctx, *, text: str):
        """ AAAAAAAAA!
        Everything you type after yell will of course, be yelled
        """
        t_upper = text.upper().replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"⬆️ {t_upper}")

    @commands.command()
    async def whisper(self, ctx, *, text: str):
        """ Shh
        Be quiet..
        """
        t_lower = text.lower().replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"⬇️ {t_lower}")

    @commands.command()
    async def echo(self, ctx, *, text: str):
        """
        Whatever you say!
        """
        t_echo = text.replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"{t_echo}")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def headpat(self, ctx):
        """Posts a random headpat from headp.at"""

        def url_to_bytes(url):
            data = requests.get(url)
            content = io.BytesIO(data.content)
            filename = url.rsplit("/", 1)[-1]
            return {"content":content, "filename":filename}

        pats = requests.get("http://headp.at/js/pats.json").json()
        pat = random.choice(pats)
        file = url_to_bytes("http://headp.at/pats/{}".format(pat))
        await ctx.send(file=discord.File(file["content"], file["filename"]))

    @commands.command()
    async def hug(self, ctx, user: discord.Member = None):
        """ Hug a user! """
        if user is None:
            user = ctx.author

        await ctx.send(f"💖 | **{ctx.author.name}** hugs **{user.name}**")

    @commands.command()
    async def cookie(self, ctx, user: discord.Member = None):
        """ Hug a user! """
        if user is None:
            user = ctx.author

        await ctx.send(f"🍪 | **{ctx.author.name}** gives **{user.name}** a cookie!")

    @commands.command()
    async def stab(self, ctx, user: discord.Member = None):
        """ Ssstab a perssson! """
        if user is None:
            user = ctx.author

        await ctx.send(f"🔪 | **{ctx.author.name}** stabbed **{user.name}** in the hand (How rude)!")

    @commands.command()
    async def pat(self, ctx, user: discord.Member = None):
        """ Headpats for all! """
        if user is None:
            user = ctx.author

        await ctx.send(f"<a:patkyutie:444890889513598986> | **{ctx.author.name}** pats **{user.name}** on the head!")

    @commands.command()
    async def nom(self, ctx, user: discord.Member = None):
        """ Nom a user! """
        if user is None:
            user = ctx.author

        await ctx.send(f"<a:WanTriggered:437201280918618112> | **{ctx.author.name}** nommed **{user.name}**'s arm!")

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def owoify(self, ctx):
        """ owo text """
        text = ctx.message.content[9:] #Really shitty bodge to make this work properly
        if len(text) == 0 or len(text) > 1500:
            await ctx.send("That string is too long or too short!")
            return
        await self.textapi(ctx, f'https://nekos.life/api/v2/owoify?text={text}', 'owo')

    @commands.command()
    @commands.cooldown(rate=1, per=5.0, type=commands.BucketType.user)
    async def fact(self, ctx):
        """ sends a random fact """
        await self.factapi(ctx, 'https://nekos.life/api/v2/fact', 'fact')

    @commands.command()
    async def bamboozle(self, ctx):
        """ You just got bamboozled! """
        await ctx.send(f"**{ctx.author.name}** just got heckin' bamboozled!")

    @commands.command(hidden=True)
    async def highcontrastphotooffruitfloatingthreateninglyinthedark(self, ctx):
        """ .. """
        await ctx.send("https://i.imgur.com/gtm1VKQ.jpg")

    @commands.command(hidden=True)
    async def lighttheme(self, ctx):
        """ E """
        await ctx.send("Ew https://i.imgur.com/fbIE97N.png")

    @commands.command()
    async def password(self, ctx):
        """ Generates a random password string for you """
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with your random generated password **{ctx.author.name}**")
        await ctx.author.send(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(18)}")


def setup(bot):
    bot.add_cog(Fun_Commands(bot))
