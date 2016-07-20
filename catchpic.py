#coding=gb2312
import re
import urllib
import os
import MySQLdb
import time
import random
import hashlib
import traceback

#数据库判断
def db(flag,path,title,value,tbname):
    conn = MySQLdb.connect(host='host',user='user',passwd='passwd',db='dbname')
    cursor = conn.cursor()
    sel = "select flag from " + tbname + " where flag = '"+ flag +"'" 
    cursor.execute(sel)
    s = cursor.fetchall()
    if s:
        return 0
    else:   
        sql = 'insert into ' + tbname + '(flag,value,title,path) values(%s,%s,%s,%s)'
        param = (flag, value, title, path)
        n = cursor.execute(sql,param)
        if n == 1:
            return 1
            conn.commit()
    cursor.close()
    conn.colose()
    
#获取网页内容
def gethtml(url):
    html_content = urllib.urlopen(url)
    res = html_content.read()
    return res

#获取图片链接
def getpic(html,reg):
    imgcom = re.compile(reg)
    imgurl = re.findall(imgcom,html)
    return imgurl

#文件名称随机生成
def file_name():
    #使用时间戳与0到9999999随机数使用md5加密，用于给生成的文件命名避免名称重复
    m2 = hashlib.md5()
    m2.update(str(time.time()) + str(random.randint(0,9999999)) + str(random.randint(0,9999999)))
    hashmd5 = m2.hexdigest()
    return hashmd5


#下载图片
def downloadpic(pic_url,path,flag,flags,title,tbname,ctype):
    path_exists = os.path.exists(path)
    if not path_exists:
        os.makedirs(path)    
    i = 2
    while 1:
        url = pic_url + str(i) + '.html'
        html = gethtml(url)
        reg = r'<img alt=".*" src="(.*\.jpg)" \/>'
        res = getpic(html,reg) 
        if not res:
            print ctype + ' ' + flags + ' complete'
            break
        else:
            for imgurl in res:
                #s_path
                f = str(file_name())
                s_path = c_type+'/'+flags+ '/'+ f +'.jpg'
                r_flag = flag + '0'+str(i)
                value = c_type+'/'+flags+'.html'
                res = db(r_flag,s_path,title,value,tbname)
                if res == 1:
                    urllib.urlretrieve(imgurl,path + f + '.jpg')
                    print 'image' + ' '+ ctype + ' ' + r_flag + ' complete'
                else:
                    print 'image' + ' '+ ctype + ' ' + r_flag + ' download fail'
        i+=1



#字符串处理和数据库字段判断是否存在
def str_deal(res,url,c_type):
    reg = r''+ url +'(\d+)'
    #数据库表名    
    tbname = 'gpic_' + c_type
    title = '000'
    num = getpic(res,reg)
    pic_url = url + num[0] + '_'
    flag = num[0] + '_'
    flags = num[0]
    
#   path_root = 'C:/Webserver/Apache24/htdocs/girlpic/gpic/Public/Source/images/'
    path_root = 'D:/wamp/www/gpic/Public/Source/images/'
    path_end = c_type+'/' + flags + '/'
    path = path_root + path_end
    downloadpic(pic_url,path,flag,flags,title,tbname,c_type)
        
'''
抓取地址：http://www.mm131.com
抓取内容：抓取'清纯美眉'主页最新内容，总计20篇

'''
t = {'xinggan':'6','qingchun':'1','xiaohua':'2','chemo':'3','qipao':'4','mingxing':'5'}

c_type = 'qingchun'
listpage = t['qingchun']
#清纯美眉链接
url = 'http://www.mm131.com/' + c_type + '/'
#获取清纯美眉主页内容
html = gethtml(url)
reg = r'<dd><a target="_blank" href="('+url+'\d+\.html)"><img'

rurl = getpic(html,reg)
for res in rurl:
    str_deal(res,url,c_type)

nt = r'<a href=\'(list_'+ listpage +'_\d+\.html)\' class="page-en">下一页</a>'
nt_num = getpic(html,nt)
while 1:

    try:
        nt_url = url + nt_num[0]
        nt_html = gethtml(nt_url)

        #匹配清纯美眉主页第一页内容图片展示的链接
        rurl = getpic(nt_html,reg)
        for h_url in rurl:
            str_deal(h_url,url,c_type)

        nt_num = getpic(nt_html,nt)
        nt_url = url + nt_num[0]
        nt_html = gethtml(nt_url)
    except Exception,e:
#如果越界了就退出
        break
