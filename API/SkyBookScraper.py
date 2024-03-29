import requests
from requests import get
import time
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
from multiprocessing import Pool
from user_agent import generate_user_agent
import numpy as np
import json
from Utilities import ConvertAmericanOddsToDecimal

def skyBookBaseScraper(myurl, masterdata):
	# generate a user agent
	
	referer='https://www.google.com/'
	h = {'User-Agent': generate_user_agent(device_type="desktop", os=('mac', 'linux')),
		'referer': referer}
	# pause for delay second to not do too many requests to server
	delays = [.5, .33, 3, 2, 1, 1.5]
	delay = np.random.choice(delays)
	#time.sleep(delay)
	

	
	try:
		source = get(myurl, timeout=5, headers=h)
	except Exception as e:
		print(str(e))
		print('SkyBook connnetion error')
		return
	source=source.text.split('(')[1]
	source=source.strip()
	source=source[:-1]
	
	source=json.loads(source)
		
		
	
	for game in source['games']:
		lines=game['lines']
		if len(lines)==0:
			continue
		team_1 = game['vtm']
		team_2 = game['htm']
		sport=game['idspt']
		if sport=="NFL" or sport=="CFB":
			sport="football"
		elif sport=="MLB":
			sport="baseball"
		elif sport=="NBA" or sport=="CBB":
			sport="basketball"
		elif sport=="NHL":
			sport="hockey"
		elif sport=="MU":
			sport="fighting"
		sport=sport.lower()
		
		sport=(str(sport.encode("utf-8")))
		linetype=game['gpd']
		if linetype=="GAME":
			linetype="Match"
		elif linetype=="SECOND HALF":  
			linetype="2nd Half"
			team_2=team_2[3:]
			team_1=team_1[3:]
		elif linetype=="FIRST HALF":
			linetype="1st Half"
			team_2=team_2[3:]
			team_1=team_1[3:]
		elif linetype=="FIRST QUARTER":
			linetype="1st Quarter"
			team_2=team_2[3:]
			team_1=team_1[3:]
		elif linetype=="SECOND QUARTER":
			linetype="2nd Quarter"
			team_2=team_2[3:]
			team_1=team_1[3:]
		elif linetype=="THIRD  QUARTER":
			linetype="3rd Quarter"
			team_2=team_2[3:]
			team_1=team_1[3:]
		elif linetype=="FOURTH QUARTER":
			linetype="4th Quarter"
			team_2=team_2[3:]
			team_1=team_1[3:]
		team_1=team_1.lower()
		team_2=team_2.lower()
		team_1=str(team_1.encode("utf-8"))
		team_2=str(team_2.encode("utf-8"))	
		matchup={}
		for line in lines:
			try:
				try: 
					odd_1_1 = line['vsprdt']
					matchup["AwayTeamPointSpread"]=odd_1_1
				except KeyError: pass
				try: 
					odd_1_2 = line['vsprdoddst']
					if odd_1_2>0 :
						odd_1_2="+"+str(odd_1_2)
					matchup["AwayTeamPointLineAmerican"]=odd_1_2
					odd_1_2=ConvertAmericanOddsToDecimal(odd_1_2)
					matchup["AwayTeamPointLine"]=odd_1_2
				except KeyError: pass
				try: 
					moneyline1=line['voddst']
					if moneyline1>0 :
						moneyline1="+"+str(moneyline1)
					matchup["AwayTeamMoneyLineAmerican"]=moneyline1
					moneyline1=ConvertAmericanOddsToDecimal(moneyline1)
					matchup["AwayTeamMoneyLine"]=moneyline1
				except KeyError: pass
				try: 
					over=line['unt']
					matchup["OverPoints"]=over
				except KeyError: pass
				try: 
					overline=line['ovoddst']
					if overline>0 :
						overline="+"+str(overline)
					matchup["OverLineAmerican"]=overline
					overline=ConvertAmericanOddsToDecimal(overline)
					matchup["OverLine"]=overline
				except KeyError: pass
				try: 
					odd_2_1 = line['hsprdt']
					matchup["HomeTeamPointSpread"]= odd_2_1
				except KeyError: pass
				try: 
					odd_2_2 = line['hsprdoddst']
					if odd_2_2>0 :
						odd_2_2="+"+str(odd_2_2)
					matchup["HomeTeamPointLineAmerican"]=odd_2_2
					odd_2_2=ConvertAmericanOddsToDecimal(odd_2_2)
					matchup["HomeTeamPointLine"]=odd_2_2
				except KeyError: pass
				try: 
					moneyline2=line['hoddst']
					if moneyline2>0 :
						moneyline2="+"+str(moneyline2)
					matchup["HomeTeamMoneyLineAmerican"]=moneyline2
					moneyline2=ConvertAmericanOddsToDecimal(moneyline2)
					matchup["HomeTeamMoneyLine"]=moneyline2
				except KeyError: pass
				try: 
					under=line['unt']
					matchup["UnderPoints"]=under
				except KeyError: pass
				try: 
					underline=line['unoddst']
					if underline>0 :
						underline="+"+str(underline)
					matchup["UnderLineAmerican"]=underline
					underline=ConvertAmericanOddsToDecimal(underline)
					matchup["UnderLine"]=underline
				except KeyError: pass
				
				
				matchup["LineType"]=linetype
				matchup["SportsBook"]="SkyBook"
				matchup["HomeTeam"]=team_2
				matchup["AwayTeam"]=team_1
				matchup["Sport"]=sport
				
				key=sport+ " "+team_1+" vs "+team_2
				
				
				if (key in masterdata.keys()):
					l=masterdata[key]
					l.append(matchup)
					masterdata[key]=l

				else:
					l=[]
					l.append(matchup)
					masterdata[key]=l

				
				
			except IndexError:
				continue
	return
