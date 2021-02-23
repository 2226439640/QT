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
from PySide2.QtCore import QFile, QDate
import threading
import pyqtgraph as pg
from signals import Signals


class Fund:
    def __init__(self):
        file = QFile('./fund.ui')
        file.open(QFile.ReadOnly)
        file.close()

        loader = QUiLoader()
        loader.registerCustomWidget(pg.PlotWidget)
        self.ui =loader.load(file)
        self.signals = Signals()
        self._fundUrl = 'http://fund.eastmoney.com/data/rankhandler.aspx'
        self.FundDict = {}
        with open('Funds.json', mode='r', encoding='utf-8') as fp:
            self.FundDict = json.load(fp)

        self.ui.search.textChanged.connect(self.findFund)
        self.ui.search.returnPressed.connect(lambda: self.ui.fundsCB.addItems([self.FundDict[self.ui.search.text()]]))
        # self.ui.updateButton.clicked.connect(self.getAllFunds)
        self.ui.pushButton_2.clicked.connect(self.DWJZ_update)

        self.ui.widget.setTitle('历史净值', color='008080', size='12pt')
        self.ui.widget.setLabel('left', '净值')
        self.ui.widget.setLabel('bottom', '时间')
        self.ui.widget.setBackground('w')
        self.signals.LSJZ.connect(self.showLSJZ)

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

    def DWJZ_update(self):
        start_date = self.ui.sdEdit.date().toString('yyyy-MM-dd')
        end_date = self.ui.edEdit.date().toString('yyyy-MM-dd')
        thread = threading.Thread(target=self.getDWJZ, args=(self.ui.search.text(), start_date, end_date))
        thread.start()

    def getDWJZ(self, JZNo, sdate, edate):
        url = 'http://api.fund.eastmoney.com/f10/lsjz'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/87.0.4280.66 Safari/537.36',
            'Referer': 'http://fundf10.eastmoney.com/jjjz_%s.html' % JZNo
        }
        data = {
            'callback': 'jQuery18303239680339937132_1614049287312',
            'fundCode': JZNo,
            'pageIndex': '1',
            'pageSize': '20',
            'startDate': sdate,
            'endDate': edate,
            '_': '1614049334689'
        }
        res = requests.get(url, headers=headers, params=data)
        res.encoding = res.apparent_encoding
        total = re.findall('"TotalCount":(\d+)', res.text)[0]
        data['pageSize'] = int(total)
        res = requests.get(url, headers=headers, params=data)
        res.encoding = res.apparent_encoding
        date_JJJZ = re.findall('(\d{4}-\d{2}-\d{2})|"DWJZ":"(\d+\.\d*)"', res.text)
        self.signals.LSJZ.emit(date_JJJZ)

    def showLSJZ(self, data):
        date, JJJZ = [int(''.join(d[0].split('-'))) for d in data[::2]], [float(d[1]) for d in data[1::2]]
        print(date)
        print(JJJZ)
        print(len(data), len(JJJZ))
        self.ui.widget.plot(date, JJJZ, pen=pg.mkPen('b'))


if __name__ == '__main__':
    app = QApplication()
    f = Fund()
    f.ui.show()
    app.exec_()