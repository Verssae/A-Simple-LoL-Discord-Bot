# A-Simple-LoL-Discord-Bot
소환사 레벨, 랭크, 승/패, 현재 게임 중인 챔피언 보기 및 추적 기능 지원

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

    [버전](https://ddragon.leagueoflegends.com/api/versions.json) 에서 최신 버전을 찾아 (예: 9.15.1) 아래 링크의 6.24.1 대신 입력하고 다운로드하여 메인 폴더에 저장 및` config.json`의 `version`에 버전 기입

    수정할 링크: https://ddragon.leagueoflegends.com/cdn/dragontail-6.24.1.tgz

## 실행

`python bot.py`

