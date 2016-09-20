# -*- coding:utf-8 -*-
from lxml import etree
import urllib2
from multiprocessing.dummy import Pool as ThreadPool
import MySQLdb
import random
import smtplib
from email.mime.text import MIMEText
import hashlib
import time

class CrawlJG:


    def __init__(self, db, mail):
        self.db = db
        self.mail = mail
        self.userAgent = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
            'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
            'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
            'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        ]
    # def changeProxy(self, proxyList):
    #     proxy = random.choice(proxyList)
    #     if proxy == None:
    #         proxyHandler = urllib2.ProxyHandler({})
    #     else:
    #         proxyHandler = urllib2.ProxyHandler({'http' : proxy})
    #     opener = urllib2.build_opener(proxyHandler)
    #     urllib2.install_opener(opener)
    #     print u'智能切换代理：%s' % (u'本机' if proxy == None else proxy)

    #获取页面主体
    def getHtmlBody(self, url):
        proxy = ['14.101.41.162:8080', '203.176.136.42:8080', '151.243.121.235:8080', None]

        c_userAgent = random.choice(self.userAgent)
        headers = {'User-Agent' : c_userAgent}
        try:
            # self.changeProxy(proxy)
            request = urllib2.Request(url, headers = headers)
            response = urllib2.urlopen(request)

            return response.read()
        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"连接金光布袋戏失败,错误原因",e.reason
                return None

    #金光布袋戏剧目列表
    def getNameUrlLists(self, htmlBody):

        nameUrlLists = []       #金光布袋戏剧目url列表

        #解析到a节点
        xpathPattern = '//div[@class="lm_box"]/a'
        selector = etree.HTML(htmlBody)
        nameUrls = selector.xpath(xpathPattern)
        nameId = len(nameUrls)              #剧目序列号

        for nameUrl in nameUrls:

            name = nameUrl.xpath('@title')[0].encode('utf-8')
            href = nameUrl.xpath('@href')[0].encode('utf-8')
            nameUrlDict = {'name' : name, 'url' : href, 'name_id': nameId}    #金光布袋戏单个剧目名称、url指向
            nameUrlLists.append(nameUrlDict)
            nameId -= 1

        return nameUrlLists




    #获取集数列表
    def getEpisodeUrlLists(self, nameUrl):
        oneEpisodeUrlList = []     #获取一部金光布袋戏的集数url列表

        htmlBody = self.getHtmlBody(nameUrl['url'])
        #解析到div节点
        xpathPattern = '//div[@class="c_box"]'
        selector = etree.HTML(htmlBody)
        episodeUrls = selector.xpath(xpathPattern)

        for episodeUrl in episodeUrls:
            href = episodeUrl.xpath('a/@href')[0].encode('utf-8')

            episode = episodeUrl.xpath('a/@title')[0].encode('utf-8')
            p_time = episodeUrl.xpath('span/text()')[0].encode('utf-8')

            oneEpisodeUrlList.append({'name_id': nameUrl['name_id'], 'url' : href, 'episode' : episode, 'time' : p_time})
        return {'name' : nameUrl['name'], 'name_id' : nameUrl['name_id'],'details' : oneEpisodeUrlList}

    #获取每集播放地址
    def getVideoLists(self, episodeUrls):

        oneVideoUrlLists = []
        for detail in episodeUrls['details']:
            htmlBody = self.getHtmlBody(detail['url'])
            xpathPattern = '//div[@class="left_a"]/embed/@src'
            selector = etree.HTML(htmlBody)
            videoUrl = selector.xpath(xpathPattern)
            if len(videoUrl) > 0:
                oneVideoUrlLists.append({
                        'name_id': detail['name_id'],
                        'url' : videoUrl[0].encode('utf-8'),
                        'episode' : detail['episode'],
                        'time' : detail['time']
                    })


            else:
                break
        return {'name' : episodeUrls['name'], 'name_id' : episodeUrls['name_id'], 'details' : oneVideoUrlLists}

    def threadPool(self, method, params, poolNum = 8):
        pool = ThreadPool(poolNum)
        result = pool.map(method, params)
        pool.close()
        pool.join()
        return result

    #爬虫入口
    def startCrawlJG(self):

        url = 'http://video.yaodaojiao.com/jinguang/'
        htmlBody = self.getHtmlBody(url)
        nameUrlLists = self.getNameUrlLists(htmlBody)
        episodeUrlLists = self.threadPool(self.getEpisodeUrlLists, nameUrlLists)
        episodeVideoLists = self.threadPool(self.getVideoLists, episodeUrlLists)

        return episodeVideoLists

    def writeAndEmail(self, episodeVideoLists):

        exitVideoNames = self.db.fetchAll('select `name` from `video_name`')
        topVideoName = exitVideoNames[0]['name'] if len(exitVideoNames) > 0 else None
        exitEpisodeUrls = self.db.fetchAll('select `url` from `episode_details`')
        topEpisodeUrl = exitEpisodeUrls[0]['url'] if len(exitEpisodeUrls) > 0 else None

        lateIndex = 0
        for video in episodeVideoLists:
            if video['name'] != topVideoName:
                self.db.insert('video_name', {
                    'name_id' : video['name_id'],
                    'name' : video['name'],
                    'md5_name' : hashlib.md5(video['name']).hexdigest(),
                    'video_num' : len(video['details'])
                })

            for detail in video['details']:
                if detail['url'] != topEpisodeUrl:
                    self.db.insert('episode_details', detail)
                    if lateIndex < 3:
                        msg = self.mail.msgTmpl(detail['episode'], detail['url'])
                        self.mail.sender(msg, ['1720938946@qq.com'], '金光布袋戏更新呢,快来看')
                        lateIndex += 1

class DB:
    def __init__(self, DB_HOST,  DB_USER, DB_PWD, DB_NAME, DB_PORT=3306, DB_CHARSET='utf-8'):
        self.DB_HOST = DB_HOST
        self.DB_USER = DB_USER
        self.DB_PWD = DB_PWD
        self.DB_PORT = DB_PORT
        self.DB_CHARSET = DB_CHARSET
        self.DB_NAME = DB_NAME

        self.conn = self.getConnection()
        self.selectDB(self.DB_NAME)
        self.cur = self.conn.cursor()

    def __del__(self):
        self.close()

    def close(self):
        self.cur.close()
        self.conn.close()

    def getConnection(self):
        try:
            return MySQLdb.Connect(
                           host=self.DB_HOST, #设置MYSQL地址
                           port=self.DB_PORT, #设置端口号
                           user=self.DB_USER, #设置用户名
                           passwd=self.DB_PWD, #设置密码
                           charset='utf8' #设置编码
                           )
        except MySQLdb.Error as e:
            print "Connect Mysql Error %d: %s" % (e.args[0], e.args[1])

    def selectDB(self, db):
        try:
            return self.conn.select_db(db)
        except MySQLdb.Error as e:
            print "Select db Error %d: %s" % (e.args[0], e.args[1])

    def fetchAll(self, sqlString):
        try:
            self.cur.execute(sqlString)
            result=self.cur.fetchall()
            desc =self.cur.description
            d = []
            for inv in result:
                _d = {}
                for i in range(0,len(inv)):
                    _d[desc[i][0]] = inv[i]
                    d.append(_d)
            return d
        except MySQLdb.Error as e:
            print "Query db Error %s" % sqlString
            return None

    #插入数据
    #tableName 表名称
    #data 数据字典
    def insert(self, tableName, data):
        try:
            prefix = "" . join(['INSERT INTO', ' ', '`', tableName, '`'])
            columns = data.keys()
            fields = "," . join(["".join(['`', column, '`']) for column in columns])
            values = "," . join(["%s" for i in range(len(columns))])
            sqlString = "" . join([prefix, "(", fields, ") VALUES (", values, ")"])
            params = [data[key] for key in columns]

            self.cur.execute(sqlString, params)         #原作者把这里使用tuple(params)
            self.conn.commit()
            return True
        except MySQLdb.Error as e:
            print "Insert Data Error %s\nSQL:%s" % (e, sqlString)
            self.conn.rollback()
            return False

    # #转化查询结果为列表Sqlr
    # def fetchAll(self):
    #     result=self.cur.fetchall()
    #     desc =self.cur.description
    #     d = []
    #     for inv in result:
    #         print len(inv)
    #         _d = {}
    #         for i in range(0, len(inv)):
    #             print i
    #     #         _d[desc[i][0]] = str(inv[i])
    #     #     d.append(_d)
    #     # return d
    #
    #
    # def update(self, sqlString):
    #     cursor=self.conn.cursor()
    #     cursor.execute(sqlString)
    #     self.conn.commit()
    #     cursor.close()
    #     self.conn.close()

class Mail:
    def __init__(self, MAIL_HOST,  MAIL_USER, MAIL_PWD, MAIL_POSTFIX='163.com', MAIL_PORT=25):
        self.MAIL_HOST = MAIL_HOST
        self.MAIL_USER = MAIL_USER
        self.MAIL_PWD = MAIL_PWD
        self.MAIL_POSTFIX = MAIL_POSTFIX
        self.MAIL_PORT = MAIL_PORT

        try:
            self.smtpHandler = smtplib.SMTP()
            self.smtpHandler.connect(self.MAIL_HOST, self.MAIL_PORT)
            self.smtpHandler.login(self.MAIL_USER, self.MAIL_PWD)
            print 'Connect Ok'
        except smtplib.SMTPException:
            print "Connect SMTP Error: %s" % self.MAIL_HOST

    def __del__(self):
        self.smtpHandler.quit()

    #发送邮件
    #开始发送不成功是因为From跟To设置有问题
    def sender(self,  message, mailToLists, subject, subtype='html'):
        try:
            me = self.MAIL_USER + '@' + self.MAIL_POSTFIX
            self.message = MIMEText(message, subtype)
            self.message['From'] = me
            self.message['To'] = ";".join(mailToLists)
            self.message['Subject'] = subject
            self.smtpHandler.sendmail(me, mailToLists, self.message.as_string())
            print 'Send Email Ok'
            return True
        except smtplib.SMTPException as e:
            print 'Send Email Fail'
            return False

    #简单信息模板
    def msgTmpl(self, episode, url):
        msg = '<p>更新喽，还不赶紧去看看</p><p><a href="' + url + '"><span>' + episode + '</span></a></p>'
        return msg

if __name__ == '__main__':

    crawler = CrawlJG(DB('127.0.0.1',   'root', '', 'video_jg'), Mail('smtp.163.com', 'whutwf18', 'XiaoFeiRen18'))
    start = time.clock()
    videoUrls = crawler.startCrawlJG()
    crawler.writeAndEmail(videoUrls)
    end = time.clock()
    print end - start