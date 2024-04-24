import requests
import urllib3
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta

#function for getting individual fight stats
def get_fight_stats(url, timeout=30):
    page = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(page.content, "html.parser")
    fd_columns = {'fighter':[], 'knockdowns':[],'sig_strikes':[], 'total_strikes':[], 'takedowns':[], 'sub_attempts':[], 'pass':[],
                   'reversals':[]}
    
    #gets overall fight details
    fight_details = soup.select_one('tbody.b-fight-details__table-body')
    if fight_details == None:
        print('missing fight details for:', url)
        return None
    else:
        fd_cols = fight_details.select('td.b-fight-details__table-col')
        for i in range(len(fd_cols)):
            #skip 3 and 6: strike % and takedown %, will calculate these later
            if i == 3 or i == 6:
                pass
            else:
                col = fd_cols[i].select('p')
                for row in col:
                    data = row.text.strip()
                    if i == 0: #add to fighter
                        fd_columns['fighter'].append(data)
                    elif i == 1: #add to sig strikes
                        fd_columns['knockdowns'].append(data)
                    elif i == 2: #add to total strikes
                        fd_columns['sig_strikes'].append(data)
                    elif i == 4: #add to total strikes
                        fd_columns['total_strikes'].append(data)
                    elif i == 5: # add to takedowns
                        fd_columns['takedowns'].append(data)
                    elif i == 7: # add to sub attempts
                        fd_columns['sub_attempts'].append(data)
                    elif i == 8: # add to passes
                        fd_columns['pass'].append(data)
                    elif i == 9: # add to reversals
                        fd_columns['reversals'].append(data)
        ov_details = pd.DataFrame(fd_columns)

        #get sig strike details
        sig_strike_details = soup.find('p', class_ = 'b-fight-details__collapse-link_tot',text = re.compile('Significant Strikes')).find_next('tbody', class_ = 'b-fight-details__table-body')
        sig_columns = {'fighter':[], 'head_strikes':[], 'body_strikes':[],'leg_strikes':[], 'distance_strikes':[],
                   'clinch_strikes':[], 'ground_strikes':[]}
        fd_cols = sig_strike_details.select('td.b-fight-details__table-col')
        for i in range(len(fd_cols)):
            #skip 1, 2 (sig strikes, sig %)
            if i == 1 or i == 2:
                pass
            else:
                col = fd_cols[i].select('p')
                for row in col:
                    data = row.text.strip()
                    if i == 0: #add to fighter
                        sig_columns['fighter'].append(data)
                    elif i == 3: #add to head strikes
                        sig_columns['head_strikes'].append(data)
                    elif i == 4: #add to body strikes
                        sig_columns['body_strikes'].append(data)
                    elif i == 5: #add to leg strikes
                        sig_columns['leg_strikes'].append(data)
                    elif i == 6: #add to distance strikes
                        sig_columns['distance_strikes'].append(data)
                    elif i == 7: #add to clinch strikes
                        sig_columns['clinch_strikes'].append(data)
                    elif i == 8: #add to ground strikes
                        sig_columns['ground_strikes'].append(data)
        sig_details = pd.DataFrame(sig_columns)

        cfd = pd.merge(ov_details, sig_details, on = 'fighter', how = 'left', copy = False)

        cfd['takedowns_landed'] = cfd.takedowns.str.split(' of ').str[0].astype(int)
        cfd['takedowns_attempts'] = cfd.takedowns.str.split(' of ').str[-1].astype(int)
        cfd['sig_strikes_landed'] = cfd.sig_strikes.str.split(' of ').str[0].astype(int)
        cfd['sig_strikes_attempts'] = cfd.sig_strikes.str.split(' of ').str[-1].astype(int)
        cfd['total_strikes_landed'] = cfd.total_strikes.str.split(' of ').str[0].astype(int)
        cfd['total_strikes_attempts'] = cfd.total_strikes.str.split(' of ').str[-1].astype(int)
        cfd['head_strikes_landed'] = cfd.head_strikes.str.split(' of ').str[0].astype(int)
        cfd['head_strikes_attempts'] = cfd.head_strikes.str.split(' of ').str[-1].astype(int)
        cfd['body_strikes_landed'] = cfd.body_strikes.str.split(' of ').str[0].astype(int)
        cfd['body_strikes_attempts'] = cfd.body_strikes.str.split(' of ').str[-1].astype(int)
        cfd['leg_strikes_landed'] = cfd.leg_strikes.str.split(' of ').str[0].astype(int)
        cfd['leg_strikes_attempts'] = cfd.leg_strikes.str.split(' of ').str[-1].astype(int)
        cfd['distance_strikes_landed'] = cfd.distance_strikes.str.split(' of ').str[0].astype(int)
        cfd['distance_strikes_attempts'] = cfd.distance_strikes.str.split(' of ').str[-1].astype(int)
        cfd['clinch_strikes_landed'] = cfd.clinch_strikes.str.split(' of ').str[0].astype(int)
        cfd['clinch_strikes_attempts'] = cfd.clinch_strikes.str.split(' of ').str[-1].astype(int)
        cfd['ground_strikes_landed'] = cfd.ground_strikes.str.split(' of ').str[0].astype(int)
        cfd['ground_strikes_attempts'] = cfd.ground_strikes.str.split(' of ').str[-1].astype(int)

        cfd = cfd.drop(['takedowns','sig_strikes', 'total_strikes', 'head_strikes', 'body_strikes', 'leg_strikes', 'distance_strikes', 
                        'clinch_strikes', 'ground_strikes'], axis = 1)
        return(cfd)

#function for getting fight stats for all fights on a card
def get_fight_card(url, timeout=30):
    page = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(page.content, "html.parser")
    
    fight_card = pd.DataFrame()
    date = soup.select_one('li.b-list__box-list-item').text.strip().split('\n')[-1].strip()
    rows = soup.select('tr.b-fight-details__table-row')[1:]
    for row in rows:
        fight_det = {'date':[], 'fight_url':[], 'event_url':[], 'result':[], 'fighter':[], 'opponent':[], 'division':[], 'method':[],
                    'round':[], 'time':[], 'fighter_url':[], 'opponent_url':[]}
        fight_det['date'] += [date, date] #add date of fight
        fight_det['event_url'] += [url, url] #add event url
        cols = row.select('td')
        for i in range(len(cols)):
            if i in set([2,3,4,5]): #skip sub, td, pass, strikes
                pass
            elif i == 0: #get fight url and results
                fight_url = cols[i].select_one('a')['href'] #get fight url
                fight_det['fight_url'] += [fight_url, fight_url]

                results = cols[i].select('p')
                if len(results) == 2: #was a draw, table shows two draws
                    fight_det['result'] += ['D', 'D']
                else: #first fighter won, second lost
                    fight_det['result'] += ['W', 'L'] 

            elif i == 1: #get fighter names and fighter urls
                fighter_1 = cols[i].select('p')[0].text.strip()
                fighter_2 = cols[i].select('p')[1].text.strip()
                
                fighter_1_url = cols[i].select('a')[0]['href']
                fighter_2_url = cols[i].select('a')[1]['href']

                fight_det['fighter'] += [fighter_1, fighter_2]
                fight_det['opponent'] += [fighter_2, fighter_1]
                
                fight_det['fighter_url'] += [fighter_1_url, fighter_2_url]
                fight_det['opponent_url'] += [fighter_2_url, fighter_1_url]
            elif i == 6: #get division
                division = cols[i].select_one('p').text.strip()
                fight_det['division'] += [division, division]
            elif i == 7: #get method
                method = cols[i].select_one('p').text.strip()
                fight_det['method'] += [method, method]
            elif i == 8: #get round
                rd = cols[i].select_one('p').text.strip()
                fight_det['round'] += [rd, rd]
            elif i == 9: #get time
                time = cols[i].select_one('p').text.strip()
                fight_det['time'] += [time, time]

        fight_det = pd.DataFrame(fight_det)
        #get striking details (with retries)
        attempts = 1
        data_pulled = False
        while attempts <=3 or not data_pulled:
            try:
                str_det = get_fight_stats(fight_url)
                data_pulled = True
            except Exception as e:
                print(f'failed getting fight stats for {fight_url} on attempt {attempts}')
                attempts += 1
        if str_det is None:
            pass
        else:
            #join to fight details
            fight_det = pd.merge(fight_det, str_det, on = 'fighter', how = 'left', copy = False)
            #add fight details to fight card
            fight_card = pd.concat([fight_card, fight_det], axis = 0)  
    fight_card = fight_card.reset_index(drop = True)
    return fight_card

#function that gets stats on all fights on all cards
def get_all_fight_stats(timeout=30):
    url = 'http://ufcstats.com/statistics/events/completed?page=all'
    page = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(page.content, "html.parser") 

    events_table = soup.select_one('tbody')
    events = [event['href'] for event in events_table.select('a')[1:]] #omit first event, future event

    fight_stats = pd.DataFrame()
    for event in events:
        print(event)
        stats = get_fight_card(event, timeout=timeout)
        fight_stats = pd.concat([fight_stats, stats], axis = 0)
        
    fight_stats = fight_stats.reset_index(drop = True)
    return fight_stats      

#gets individual fighter attributes
def get_fighter_details(fighter_urls, timeout = 30):
    fighter_details = {'name':[], 'height':[], 'reach':[], 'stance':[], 'dob':[], 'url':[]}

    for f_url in fighter_urls:
        print(f_url)
        page = requests.get(f_url, timeout=timeout)
        soup = BeautifulSoup(page.content, "html.parser")

        fighter_name = soup.find('span', class_ = 'b-content__title-highlight').text.strip()
        fighter_details['name'].append(fighter_name)
        
        fighter_details['url'].append(f_url)

        fighter_attr = soup.find('div', class_ = 'b-list__info-box b-list__info-box_style_small-width js-guide').select('li')
        for i in range(len(fighter_attr)):
            attr = fighter_attr[i].text.split(':')[-1].strip()
            if i == 0:
                fighter_details['height'].append(attr)
            elif i == 1:
                pass #weight is always just whatever weightclass they were fighting at
            elif i == 2:
                fighter_details['reach'].append(attr)
            elif i == 3:
                fighter_details['stance'].append(attr)
            else:
                fighter_details['dob'].append(attr)
    return pd.DataFrame(fighter_details)  

#updates fight stats with newer fights
def update_fight_stats(old_stats, timeout=30): #takes dataframe of fight stats as input
    url = 'http://ufcstats.com/statistics/events/completed?page=all'
    page = requests.get(url, timeout=timeout)
    soup = BeautifulSoup(page.content, "html.parser") 

    events_table = soup.select_one('tbody')
    events = [event['href'] for event in events_table.select('a')[1:]] #omit first event, future event
    
    saved_events = set(old_stats.event_url.unique())
    new_stats = pd.DataFrame()
    for event in events:
        if event in saved_events:
            break
        else:
            print(event)
            stats = get_fight_card(event, timeout=timeout)
            new_stats = pd.concat([new_stats, stats], axis = 0)
    
    updated_stats = pd.concat([new_stats, old_stats], axis = 0)
    updated_stats = updated_stats.reset_index(drop = True)
    return(updated_stats)

#updates fighter attributes with new fighters not yet saved yet
def update_fighter_details(fighter_urls, saved_fighters, timeout=30):
    fighter_details = {'name':[], 'height':[], 'reach':[], 'stance':[], 'dob':[], 'url':[]}
    fighter_urls = set(fighter_urls)
    saved_fighter_urls = set(saved_fighters.url.unique())

    for f_url in fighter_urls:
        if f_url in saved_fighter_urls:
            pass
        else:
            print('adding new fighter:', f_url)
            page = requests.get(f_url, timeout=timeout)
            soup = BeautifulSoup(page.content, "html.parser")

            fighter_name = soup.find('span', class_ = 'b-content__title-highlight').text.strip()
            fighter_details['name'].append(fighter_name)

            fighter_details['url'].append(f_url)

            fighter_attr = soup.find('div', class_ = 'b-list__info-box b-list__info-box_style_small-width js-guide').select('li')
            for i in range(len(fighter_attr)):
                attr = fighter_attr[i].text.split(':')[-1].strip()
                if i == 0:
                    fighter_details['height'].append(attr)
                elif i == 1:
                    pass #weight is always just whatever weightclass they were fighting at
                elif i == 2:
                    fighter_details['reach'].append(attr)
                elif i == 3:
                    fighter_details['stance'].append(attr)
                else:
                    fighter_details['dob'].append(attr)
    new_fighters = pd.DataFrame(fighter_details)
    updated_fighters = pd.concat([new_fighters, saved_fighters])
    updated_fighters = updated_fighters.reset_index(drop = True)
    return updated_fighters 