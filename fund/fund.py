# -*- coding:utf-8 -*-
import re
import aiohttp
import requests
import asyncio
import time
import copy
import json
from PySide2.QtWidgets import QApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile


class Fund:
    def __init__(self):
        file = QFile('./fund.ui')
        file.open(QFile.ReadOnly)
        file.close()

        self.ui = QUiLoader().load(file)
        self._fundUrl = 'http://fund.eastmoney.com/data/rankhandler.aspx'
        self.FundDict = {}
        with open('Funds.json', mode='r', encoding='utf-8') as fp:
            self.FundDict = json.load(fp)

        self.ui.search.textChanged.connect(self.findFund)
        self.ui.search.returnPressed.connect(lambda: self.ui.fundsCB.addItems([self.FundDict[self.ui.search.text()]]))
        # self.ui.updateButton.clicked.connect(self.getAllFunds)

    def getAllFunds(self):
        data = {
            'op': 'ph',
            'dt': 'kf',
            'ft': 'all',
            'rs': '',
            'gs': 0,
            'sc': '6yzf',
            'st': 'desc',
            'sd': '{}'.format(time.strftime('%Y - %m - %d', time.localtime()).replace('2021', '2020')),
            'ed': '{0}'.format(time.strftime('%Y - %m - %d', time.localtime())),
            'qdii': '',
            'tabSubtype': ', , , , ,',
            'pi': 1,
            'pn': 50,
            'dx': 1,
            'v': 0.6733488855902616
        }
        pages = self._nums(data)
        tasks = []
        for pageIndex in range(1, pages+1):
            data['pi'] = pageIndex
            tasks.append(self.getFunds(copy.deepcopy(data)))
        loop = asyncio.get_event_loop()
        print('starting............')
        loop.run_until_complete(asyncio.gather(*tasks))
        print('ending............')
        with open('Funds.json', mode='w', encoding='utf-8') as fp:
            json.dump(self.FundDict, fp, ensure_ascii=False)
        loop.close()

    def _nums(self, data) -> int:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.66 Safari/537.36',
            'Referer': 'http://fund.eastmoney.com/data/fundranking.html'
        }
        res = requests.get(self._fundUrl, headers=headers, data=data)
        res.encoding = res.apparent_encoding
        nums = re.findall('allPages:(\d+)', res.text)
        return int(nums[0])

    async def getFunds(self, data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.66 Safari/537.36',
            'Referer': 'http://fund.eastmoney.com/data/fundranking.html'
        }
        async with aiohttp.request('GET', self._fundUrl, headers=headers, data=data) as res:
            Fundstr = await res.text()
            print(Fundstr)
            Funds = re.findall(r'([\u4e00-\u9fa5]+[\s\w]*[\u4e00-\u9fa5]*)', Fundstr)
            FundsNo = re.findall(r'\d{6}', Fundstr)
            Fundsall = zip(FundsNo, Funds)
            for fund in Fundsall:
                self.FundDict[fund[0]] = fund[1]

    def findFund(self):
        text = self.ui.search.text()
        res = []
        for funds in self.FundDict.values():
            if funds.startswith(text):
                res.append(funds)
        self.ui.fundsCB.addItems(res)


if __name__ == '__main__':
    app = QApplication()
    f = Fund()
    f.ui.show()
    app.exec_()