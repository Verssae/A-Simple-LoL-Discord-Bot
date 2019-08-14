# A-Simple-LoL-Discord-Bot
소환사 레벨, 랭크, 승/패, 현재 게임 중인 챔피언 보기 및 추적 기능, 승률 등을 지원하는 디스코드 봇 

## 요구사항
`python >= 3.6`
## 설치
`pip install discord.py`
`pip install requests`
`pip install pprint`
## 추가 설정 
* Discord token
    [디스코드 개발자 포털](https://discordapp.com/developers/applications/) 에서 디스코드 봇 생성 후, 토큰을 복사하여 `config.json`의 `token`에 저장
    
* Riot games Api key
    
    [Riot Developer Portal](https://developer.riotgames.com/) 에서 로그인 후 API key 복사하여  `config.json`의 `apikey`에 저장 (24시간마다 갱신해줘야 함)
    
* 챔피언 데이터 다운로드

## 실행

`python bot.py`

실행 시 `config.json`에 적힌 버전이 낮을 경우 챔피언 데이터 다운로드 및 업데이트가 진행됨

