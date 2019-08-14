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
        self.tracked_players = []
        with open('emoji-compact.json', 'rb') as f:
            self.emojies = json.load(f)
        self.colours = {
            "IRON" : discord.Colour.from_rgb(217,215,214),
            "BRONZE" : discord.Colour.from_rgb(192,170,152),
            "SILVER" : discord.Colour.from_rgb(160,181,182),
            "GOLD" : discord.Colour.from_rgb(212,194,118),
            "PLATINUM" : discord.Colour.from_rgb(167,218,196),
            "DIAMOND" : discord.Colour.from_rgb(115,162,193),
            "MASTER" : discord.Colour.from_rgb(232,164,253),
            "GRANDMASTER" : discord.Colour.from_rgb(248,43,62),
            "CHALLENGER" : discord.Colour.from_rgb(225,225,227)
        }
                
    @commands.command(brief="개인/2인 랭크 게임")
    async def solo(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.soloq:
                em = discord.Embed(title="개인/2인 랭크 게임", colour=self.colours.get(lol_info.getSoloq('tier')))
                em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
                em.set_image(url=LoLInfo.getEmblemUrl(lol_info.getSoloq('tier'), lol_info.getSoloq('rank')))
                em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
                em.add_field(name="승리", value=f"{lol_info.getSoloq('wins')}", inline=True).add_field(name="패배", value=f"{lol_info.getSoloq('losses')}", inline=True)
                em.add_field(name="게임 수", value=f"{lol_info.getSoloq('wins')+lol_info.getSoloq('losses')}", inline=True).add_field(name="승률", value=f"{lol_info.getSoloq('wins') / (lol_info.getSoloq('wins')+lol_info.getSoloq('losses')) * 100:.2f}%", inline=True)
                em.set_footer(text=f"{lol_info.getSoloq('tier')} {lol_info.getSoloq('rank')} {lol_info.getSoloq('leaguePoints')} lp")
                if lol_info.isActive():
                    em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                    em.add_field(name="플레이중인 챔피언", value=f"{lol_info.getChampionName()[0]}", inline=True).add_field(name="플레이 시간", value=f"{lol_info.getGameTime()}")
                    em.set_thumbnail(url=LoLInfo.getChampionUrl(lol_info.getChampionName()[1]))
                message = await ctx.send(embed=em)
            else:
                await ctx.invoke(self.bot.get_command('normal'), name=name)
            if self.tracked_players != [] and lol_info.getUser('name') in map(lambda e: e['name'], self.tracked_players):
                await self.cheerup(message)

    @commands.command(brief="일반 게임 유저")
    async def normal(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            
            em = discord.Embed(title="unranked")
            em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
            em.set_image(url=LoLInfo.getEmblemUrl(None, None))
            em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
            if lol_info.isActive():
                em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                em.add_field(name="플레이중인 챔피언", value=f"{lol_info.getChampionName()[0]}", inline=True).add_field(name="플레이 시간", value=f"{lol_info.getGameTime()}")
                em.set_thumbnail(url=LoLInfo.getChampionUrl(lol_info.getChampionName()[1]))
            message = await ctx.send(embed=em)
            if self.tracked_players != [] and lol_info.getUser('name') in map(lambda e: e['name'], self.tracked_players):
                await self.cheerup(message)

    
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
        
    @commands.command(brief="자유 랭크 게임")
    async def free(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.flex:
                em = discord.Embed(title="자유 랭크 게임" , colour=self.colours[f"{lol_info.getFlex('tier')}"])
                em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
                em.set_image(url=LoLInfo.getEmblemUrl(lol_info.getFlex('tier'), lol_info.getFlex('rank')))
                em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
                em.add_field(name="승리", value=f"{lol_info.getFlex('wins')}", inline=True).add_field(name="패배", value=f"{lol_info.getFlex('losses')}", inline=True)
                em.add_field(name="게임 수", value=f"{lol_info.getFlex('wins')+lol_info.getFlex('losses')}", inline=True).add_field(name="승률", value=f"{lol_info.getFlex('wins') / (lol_info.getFlex('wins')+lol_info.getFlex('losses')) * 100:.2f}%", inline=True)
                em.set_footer(text=f"{lol_info.getFlex('tier')} {lol_info.getFlex('rank')} {lol_info.getFlex('leaguePoints')} lp")
                if lol_info.isActive():
                    em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                    em.add_field(name="플레이중인 챔피언", value=f"{lol_info.getChampionName()[0]}", inline=True).insert_field_at(1, name="플레이 시간", value=f"{lol_info.getGameTime()}")
                    em.set_thumbnail(url=LoLInfo.getChampionUrl(lol_info.getChampionName()[1]))
                message = await ctx.send(embed=em)
            else:
                await ctx.invoke(self.bot.get_command('normal'), name=name)
                if self.tracked_players != [] and lol_info.getUser('name') in map(lambda e: e['name'], self.tracked_players):
                    await self.cheerup(message)

    @commands.command(brief="전략적 팀 전투")
    async def chess(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.tft:
                em = discord.Embed(title="롤토체스", colour=self.colours[f"{lol_info.getTft('tier')}"])
                em.set_author(name=f"{lol_info.getUser('name')}", icon_url=LoLInfo.getIconUrl(lol_info.getUser('profileIconId')))
                em.set_image(url=LoLInfo.getEmblemUrl(lol_info.getTft('tier'), lol_info.getTft('rank')))
                em.add_field(name="소환사 레벨", value=f"{lol_info.getUser('summonerLevel')}", inline=True)
                em.add_field(name="승리", value=f"{lol_info.getTft('wins')}", inline=True).add_field(name="패배", value=f"{lol_info.getTft('losses')}", inline=True)
                em.add_field(name="게임 수", value=f"{lol_info.getTft('wins')+lol_info.getTft('losses')}", inline=True).add_field(name="승률", value=f"{lol_info.getTft('wins') / (lol_info.getTft('wins')+lol_info.getTft('losses')) * 100:.2f}%", inline=True)
                em.set_footer(text=f"{lol_info.getTft('tier')} {lol_info.getTft('rank')} {lol_info.getTft('leaguePoints')} lp")
                if lol_info.isActive():
                    em.add_field(name="현재 플레이 중!", value=f"{lol_info.getQueueType()}", inline=True)
                message = await ctx.send(embed=em)
            else:
                await ctx.invoke(self.bot.get_command('normal'), name=name)
                if self.tracked_players != [] and lol_info.getUser('name') in map(lambda e: e['name'], self.tracked_players):
                    await self.cheerup(message)

    @commands.command(name='logout', brief='봇 연결 해제.')
    @commands.is_owner()
    async def logout(self, ctx):
        await self.bot.logout()
    
    @commands.command(name='login', hidden=True)
    @commands.is_owner()
    async def login(self, ctx):
        await self.bot.change_presence(activity=discord.Activity(name="LoL Info Support", type=0))

    @tasks.loop(seconds=60.0, count=None)
    async def track_loop(self):
        for player in self.tracked_players:
            channel_id = player['channel']
            lp = player['lp']
            name = player['name']
            print(f'tracking {name}')

            lol_info = LoLInfo(self.apikey, self.version)
            if lol_info.search(name):
                lol_info.setRankInfo()
                new_lp = lol_info.getSoloq('leaguePoints')
    
                if lol_info.getSoloq('wins') > player['wins']:
                    player['wins'] = lol_info.getSoloq('wins')
                    if new_lp > lp:
                        message = await self.bot.get_channel(channel_id).send(
                            f"`{name}님이 승리하여 +{new_lp - lp}포인트 획득!`"
                        )
                        player['lp'] = new_lp
                    elif new_lp == lp:
                        message = await self.bot.get_channel(channel_id).send(
                            f"`{name}님이 승급전에서 승리하여 승급에 가까워지고 있습니다!`"
                        )
                    else:
                        message = await self.bot.get_channel(channel_id).send(
                            f"`{name}님이 {lol_info.getSoloq('tier')} {lol_info.getSoloq('rank')} 로 승급했습니다!!`"
                        )
                        player['lp'] = new_lp
                        player['tier'] = lol_info.getSoloq('tier')
                        player['rank'] = lol_info.getSoloq('rank')
                    
                    
                elif lol_info.getSoloq('losses') > player['losses']:
                    pp('lose')
                    if new_lp > lp:
                        message = await self.bot.get_channel(channel_id).send(
                            f"`{name}님이 안타깝게도 {lol_info.getSoloq('tier')} {lol_info.getSoloq('rank')} 로 강등당했군요?`"
                        )
                        player['lp'] = new_lp
                        player['tier'] = lol_info.getSoloq('tier')
                        player['rank'] = lol_info.getSoloq('rank')

                    elif new_lp == lp:
                        message = await self.bot.get_channel(channel_id).send(
                            f"`{name}님이 다시하기를 했군요`"
                        )
                    else:
                        message = await self.bot.get_channel(channel_id).send(
                            f"`{name}님이 아쉬운 패배로 {lp - new_lp}점을 잃었습니다...`"
                        )
                        player['lp'] = new_lp

                elif lol_info.isActive() and not player['active']:
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님이 게임을 시작했습니다!! 화이팅~!`"
                    )
                    player['active'] = 'active'
                else: 
                    message = await self.bot.get_channel(channel_id).send(
                        f"`{name}님의 정보를 가져오는데 실패했습니다.`"
                    )
                ctx = await self.bot.get_context(message)
                cmd = self.bot.get_command("solo")
                await ctx.invoke(cmd, name=name)


    @commands.command(brief="1분마다 정보 갱신할 플레이어 저장")
    async def save(self, ctx, *, name):
        lol_info = LoLInfo(self.apikey, self.version)
        if lol_info.search(name):
            lol_info.setRankInfo()
            if lol_info.soloq:
                info = {
                    'name' : lol_info.getUser('name'),
                    'wins' : lol_info.getSoloq('wins'),
                    'losses' : lol_info.getSoloq('losses'),
                    'tier' : lol_info.getSoloq('tier'),
                    'rank' : lol_info.getSoloq('rank'),
                    'lp' : lol_info.getSoloq('leaguePoints'),
                    'channel' : ctx.channel.id,
                    'active' : lol_info.isActive()
                }
                self.tracked_players.append(info)
                self.track_loop.cancel()
                cmd = self.bot.get_command("solo")
                await ctx.invoke(cmd, name=name)
                self.track_loop.start()
                

def setup(bot):
    bot.add_cog(LoL(bot, apikey, version))


