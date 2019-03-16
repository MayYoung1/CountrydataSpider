"""
Created by Young on 2019/3/15 21:04
"""
"""
Created by Young on 2019/3/15 20:54
"""
import time
import requests
import os
import pandas as pd
import shutil

AREAS = ['110000', '120000', '130000', '140000', '150000', '210000', '220000', '230000', '310000', '320000', '330000',
         '340000', '350000', '360000', '370000',
         '410000', '420000', '430000', '440000', '450000', '460000', '500000', '510000', '520000', '530000', '540000',
         '610000', '620000', '630000', '640000', '650000']
PARS = ['A1301', 'A1303', 'A1304', 'A1401', 'A1403', 'A1404', 'A1405', 'A1406']
NAMES = {'A1301': '固定资产投资构成情况', 'A1303': '固定资产投资住宅建设情况', 'A1304': '固定资产投资项目情况', 'A1401': '房地产开发投资情况',
         'A1403': '房地产施工、竣工面积', 'A1404': '商品住宅施工、竣工面积', 'A1405': '办公楼施工、竣工面积', 'A1406': '商业营业用房施工、竣工面积'}
BASE_PATH = os.getcwd().replace('\\', '/')
DATA_PATH = BASE_PATH + '/data'
RESULT_PATH = DATA_PATH + '/result'

if os.path.exists(DATA_PATH):
    shutil.rmtree(DATA_PATH)

os.makedirs(DATA_PATH)
os.makedirs(RESULT_PATH)

for par in PARS:
    dfs = []
    name = NAMES[par]
    resultFile = '{}.csv'.format(name)
    resultpath = RESULT_PATH + '/' + resultFile
    for area in AREAS:
        t = time.time()
        timestamp = int(round(t * 1000))
        m = 'QueryData'
        dbcode = 'fsyd'
        rowcode = 'zb'
        colcode = 'sj'
        wds = '[{"wdcode":"reg","valuecode":"%s"}]' % area
        dfwds = '[{"wdcode":"zb","valuecode":"%s"},{"wdcode":"sj","valuecode":"2008-2018"}]' % par

        url = 'http://data.stats.gov.cn/easyquery.htm?m={}&dbcode={}&rowcode={}&colcode={}&wds={}&dfwds={}&k1={}'.format(
            m, dbcode, rowcode, colcode, wds, dfwds, timestamp)
        fileName = '{}-{}.json'.format(par, area)
        filePath = DATA_PATH + '/' + fileName
        response = requests.get(url)
        with open(filePath, 'w') as f:
            f.write(response.text)
        data = response.json()
        dataNodes = data['returndata']['datanodes']
        wdNodes = data['returndata']['wdnodes']
        region = wdNodes[1]['nodes'][0]['cname']
        cubeList = [[d['wds'][0]['valuecode'], d['wds'][2]['valuecode'],
                     d['wds'][1]['valuecode'], d['data']['data']] for d in dataNodes]
        cubeDict = {}
        columnNames = []
        for i in wdNodes[0]['nodes']:
            cname = i['cname']
            columnNames.append(cname)
        for cube in cubeList:
            if cube[0] not in cubeDict:
                cubeDict[cube[0]] = {}
            cubeDict[cube[0]][cube[1]] = cube[3]
        df = pd.DataFrame(cubeDict)
        df.columns = columnNames
        df['地区'] = region
        dfs.append(df)
        print('**********{}-{} Finished**********'.format(par, area))
    result = pd.concat(dfs)
    result.to_csv(resultpath, index_label='月份',encoding="utf_8_sig")

