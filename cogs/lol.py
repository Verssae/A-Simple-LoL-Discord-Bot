import discord
import requests
from discord.ext import commands, tasks
from pprint import pprint as pp
import json
import random
from bot import apikey, version


class LoLInfo:
    def __init__(self, apikey, version):
        self.apikey = apikey
        with open(f'dragontail-{version}/{version}/data/ko_KR/champion.json', 'rb') as f:
            self.champions = json.load(f).get("data")
            self.champs = self.champions.keys()

        self.soloq = None
        self.flex = None
        self.tft = None

    def search(self, sum_name):
        url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{0}?api_key={1}".format(
            sum_name, self.apikey)
        res = requests.get(url)
        if res.status_code != 200:
            return False
        else:
            self.summoner = res.json()
            self.encrypted_id = self.getUser('id')
            return self

    def setRankInfo(self):
        url = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{0}?api_key={1}".format(
            self.encrypted_id, self.apikey)
        res = requests.get(url)
        LeagueEntryDTOs = res.json()
        for league in LeagueEntryDTOs:
            if league.get('queueType') == 'RANKED_SOLO_5x5':
                self.soloq = league
            if league.get('queueType') == 'RANKED_TFT':
                self.tft = league
            if league.get('queueType') == 'RANKED_FLEX_SR':
                self.flex = league 


    # tier, rank, leaguePoints, wins, losses, 
    def getSoloq(self, attr):
        return self.soloq.get(attr)

    def getFlex(self, attr):
        return self.flex.get(attr)

    def getTft(self, attr):
        return self.tft.get(attr)

    def getUser(self, attr):
        # id, profileIconId, summonerLevel, name
        return self.summoner.get(attr)

    def isActive(self):
        url = "https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{0}?api_key={1}".format(
            self.encrypted_id, self.apikey)
        res = requests.get(url)
        if res.status_code != 200:
            return False
        else:
            self.currentGame = res.json()
            return True

    @staticmethod
    def getIconUrl(profileIconId):
        return f"https://opgg-static.akamaized.net/images/profile_icons/profileIcon{profileIconId}.jpg"
    
    @staticmethod
    def getEmblemUrl(tier, rank):
        ranks = {
            'I' : '_1',
            'II' : '_2',
            'III' : '_3',
            'IV' : '_4'
        }
        if not tier and not rank:
            return "https://opgg-static.akamaized.net/images/medals/default.png"
        return f"https://opgg-static.akamaized.net/images/medals/{tier.lower()}{ranks.get(rank)}.png"

    @staticmethod     
    def getChampionUrl(champion_name):
        return f"https://opgg-static.akamaized.net/images/lol/champion/{champion_name}.png?image=w_140&v=1"

    def getGameTime(self):
        seconds = self.currentGame.get("gameLength")
        m, s = divmod(seconds, 60)
        return f"{m}분 {s}초"

    def getChampionName(self):
        for player in self.currentGame.get("participants"):
            if player.get('summonerName') == self.getUser('name'):
                for champ_name in self.champions.keys():
                    key = self.champions.get(champ_name).get("key")
                    id = player.get("championId")
                    if  int(key) == int(id):
                        champion = self.champions.get(champ_name).get("name")
                        champion_en = champ_name
                        return (champion, champion_en)

    def getQueueType(self):
        print(self.currentGame.get("gameMode"))
        return self.currentGame.get("gameMode")

class LoL(commands.Cog):
    def __init__(self, bot, apikey, version):
        self.bot = bot
        self.info = None
        self.apikey = apikey
        self.version = version
        with open('emoji-compact.json', 'rb') as f:
            self.emojies = json.load(f)
                
    @commands.command(brief="솔로 큐")
    async def solo(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.soloq:
                em = discord.Embed(title="RANKED_SOLO_5x5", colour=discord.Colour.green())
                em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
                em.set_image(url=LoLInfo.getEmblemUrl(lol_info.getSoloq('tier'), lol_info.getSoloq('rank')))
                em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
                em.add_field(name="승리", value=f"{lol_info.getSoloq('wins')}", inline=True).add_field(name="패배", value=f"{lol_info.getSoloq('losses')}", inline=True)
                em.set_footer(text=f"{lol_info.getSoloq('tier')} {lol_info.getSoloq('rank')} {lol_info.getSoloq('leaguePoints')} lp")
                if lol_info.isActive():
                    em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                    em.add_field(name="플레이중인 챔피언", value=f"{lol_info.getChampionName()[0]}", inline=True).add_field(name="플레이 시간", value=f"{lol_info.getGameTime()}")
                    em.set_thumbnail(url=LoLInfo.getChampionUrl(lol_info.getChampionName()[1]))
                message = await ctx.send(embed=em)
            else:
                await ctx.invoke(self.bot.get_command('normal'), name=name)
            if lol_info.getUser('name') == 'Vtz':
                await self.cheerup(message)

    @commands.command(brief="일반 게임 유저")
    async def normal(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            
            em = discord.Embed(title="소환사 정보", colour=discord.Colour.green())
            em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
            em.set_image(url=LoLInfo.getEmblemUrl(None, None))
            em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
            if lol_info.isActive():
                em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                em.add_field(name="플레이중인 챔피언", value=f"{lol_info.getChampionName()[0]}", inline=True).add_field(name="플레이 시간", value=f"{lol_info.getGameTime()}")
                em.set_thumbnail(url=LoLInfo.getChampionUrl(lol_info.getChampionName()[1]))
            message = await ctx.send(embed=em)

    
    # emoji surport
    async def cheerup(self, message):
        num = random.randint(5,20)
        while num > 0:
            e = random.sample(self.emojies, 1)
            e[0].encode('unicode-escape')
            try:
                await message.add_reaction(e[0])
                num -= 1
            except:
                pass
        
    @commands.command(brief="자유랭")
    async def free(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.flex:
                em = discord.Embed(title="RANKED_FLEX_SR" , colour=discord.Colour.blue())
                em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
                em.set_image(url=LoLInfo.getEmblemUrl(lol_info.getFlex('tier'), lol_info.getFlex('rank')))
                em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
                em.add_field(name="승리", value=f"{lol_info.getFlex('wins')}", inline=True).add_field(name="패배", value=f"{lol_info.getFlex('losses')}", inline=True)
                em.set_footer(text=f"{lol_info.getFlex('tier')} {lol_info.getFlex('rank')} {lol_info.getFlex('leaguePoints')} lp")
                if lol_info.isActive():
                    em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                    em.add_field(name="플레이중인 챔피언", value=f"{lol_info.getChampionName()[0]}", inline=True).insert_field_at(1, name="플레이 시간", value=f"{lol_info.getGameTime()}")
                    em.set_thumbnail(url=LoLInfo.getChampionUrl(lol_info.getChampionName()[1]))
                message = await ctx.send(embed=em)
            else:
                await ctx.invoke(self.bot.get_command('normal'), name=name)

    @commands.command(brief="전략적 팀 전투")
    async def chess(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.tft:
                em = discord.Embed(title="RANKED_TFT", colour=discord.Colour.gold())
                em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
                em.set_image(url=LoLInfo.getEmblemUrl(lol_info.getTft('tier'), lol_info.getTft('rank')))
                em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
                em.add_field(name="승리", value=f"{lol_info.getTft('wins')}", inline=True).add_field(name="패배", value=f"{lol_info.getTft('losses')}", inline=True)
                em.set_footer(text=f"{lol_info.getTft('tier')} {lol_info.getTft('rank')} {lol_info.getTft('leaguePoints')} lp")
                if lol_info.isActive():
                    em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                message = await ctx.send(embed=em)
            else:
                await ctx.invoke(self.bot.get_command('normal'), name=name)

    @commands.command(name='logout', brief='Logs the bot out.')
    @commands.is_owner()
    async def logout(self, ctx):
        await self.bot.logout()
    
    @commands.command(name='login', hidden=True)
    @commands.is_owner()
    async def login(self, ctx):
        await self.bot.change_presence(activity=discord.Activity(name="훈민이 응원", type=0))

    @tasks.loop(seconds=60.0, count=None)
    async def track_loop(self):
        name = self.info.get('name')
        wins = self.info.get('wins')
        losses = self.info.get('losses')
        tier = self.info.get('tier')
        rank = self.info.get('rank')
        lp = self.info.get('lp')
        channel_id = self.info.get('channel')
        active = self.info.get('active')
        print(f'tracking {name}')
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            new_wins =  lol_info.getSoloq('wins')
            new_losses = lol_info.getSoloq('losses')
            new_lp = lol_info.getSoloq('leaguePoints')
            new_tier = lol_info.getSoloq('tier')
            new_rank = lol_info.getSoloq('rank')
            new_active = lol_info.isActive()
            if new_wins > wins:
                pp('win')
                if new_lp > lp:
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님이 승리하여 +{new_lp - lp}포인트 획득!`"
                    )
                elif new_lp == lp:
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님이 승급전에서 승리하여 승급에 가까워지고 있습니다!`"
                    )
                else:
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님이 {new_tier} {new_rank} 로 승급했습니다!!`"
                    )
                
            elif new_losses > losses:
                pp('lose')
                if new_lp > lp:
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님이 안타깝게도 {new_tier} {new_rank} 로 강등당했군요?`"
                    )
                elif new_lp == lp:
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님이 다시하기를 했군요`"
                    )
                else:
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님이 아쉬운 패배로 {lp - new_lp}점을 잃었습니다...`"
                    )
            elif new_active and not active:
                message = await self.bot.get_channel(channel_id).send(
                    f"`{name}님이 게임을 시작했습니다!! 화이팅~!`"
                )
            else: 
                return
            
            self.info['wins']= new_wins
            self.info['losses'] = new_losses
            self.info['tier'] = new_tier
            self.info['rank']=new_rank
            self.info['lp'] = new_lp
            self.info['active'] = new_active
            ctx = await self.bot.get_context(message)
            cmd = self.bot.get_command("solo")
            await ctx.invoke(cmd, name=name)


    @commands.command()
    async def save(self, ctx, *, name, brief="주기적으로 정보를 받아올 사람 저장(1명만 됨)"):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.soloq:
                self.info = {
                    'name' : lol_info.getUser('name'),
                    'wins' : lol_info.getSoloq('wins'),
                    'losses' : lol_info.getSoloq('losses'),
                    'tier' : lol_info.getSoloq('tier'),
                    'rank' : lol_info.getSoloq('rank'),
                    'lp' : lol_info.getSoloq('leaguePoints'),
                    'channel' : ctx.channel.id,
                    'active' : lol_info.isActive()
                }
                self.track_loop.cancel()
                pp(self.info)
                cmd = self.bot.get_command("solo")
                await ctx.invoke(cmd, name=name)
                self.track_loop.start()
                

def setup(bot):
    bot.add_cog(LoL(bot, apikey, version))


