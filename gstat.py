#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# File: stat.py
# Date: 2010-07-20
# Author: gashero

"""
对已有的各类笔记进行统计和过滤。
"""

import os
import sys
import re
import time

RE_IMAGE=re.compile(r'''^\s*\.\. image:: (.*?)$''',re.M)
RE_BOOKMARK=re.compile(r'''@page (\d+)-(\d+)''')

def walktree(topdir,datadict):
    """遍历目录获取所需信息"""
    for (dirpath,dirlist,fnlist) in os.walk(topdir):
        if dirpath.startswith('./.git'):
            continue
        for fn in fnlist:
            if fn.endswith('.py'):
                continue
            if fn.endswith('.rst'):
                datadict['cnt_rst']+=1
            else:
                raise ValueError('unknown file %s'%fn)
            fn_full=os.path.join(dirpath,fn)
            cur_bytes=os.path.getsize(fn_full)
            datadict['cnt_bytes']+=cur_bytes
            fi=open(fn_full,'rb')
            data=fi.read()
            fi.close()
            imagelist=RE_IMAGE.findall(data)
            if imagelist:
                bndirpath=os.path.join('../builtnote',dirpath)
                for imagefn in imagelist:
                    newfullpath=os.path.normpath(os.path.join(bndirpath,imagefn))
                    if not os.path.exists(newfullpath):
                        print 'LostImage[%s]=%s'%(fn_full,newfullpath)
            if '\r' in data:
                print 'DOSFILE: %s'%fullpath
            try:
                data_unicode=data.decode('utf-8')
            except UnicodeDecodeError:
                print 'GBKFILE: %s'%fn_full
            blank_count=data_unicode.count(' ')
            if blank_count>0 and len(data_unicode)*1.0/blank_count<2.8:
                print 'MANY BLANK: %s [%d/%d]'%(
                        fn_full,blank_count,len(data_unicode))
            if len(data_unicode)<1000:
                print 'SMALLFILE: %s [%d]'%(fn_full,len(data_unicode))
            datadict['cnt_chars']+=len(data_unicode)
            datadict['@page']+=data_unicode.count(u'@page')
            datadict['@wait']+=data_unicode.count(u'@wait')
            if len(data_unicode)>50000:
                datadict['topchars'].append((fn_full,len(data_unicode)))
            if fn.rsplit('.',1)[-1] not in ('rst','py'):
                print 'OTHERFILE: %s'%(fn_full,)
    return

def get_progress(fn_rst):
    """计算一本书的读书进度，按照@page符号来计算"""
    fi=open(fn_rst,'rU')
    data=fi.read()
    fi.close()
    maxpage=0
    unread=0
    cnt_bookmark=0
    for s,e in RE_BOOKMARK.findall(data):
        #print s,e
        s=int(s)
        e=int(e)
        maxpage=max(e,maxpage)
        unread+=(e+1-s)
        cnt_bookmark+=1
    progress={
            'maxpage':      maxpage,
            'unread':       unread,
            'cnt_bookmark': cnt_bookmark,
            }
    return progress

def newdaily(yyyyqn):
    """生成新的行程管理页面"""
    fn_daily='mindcontrol/daily/%s.rst'%yyyyqn
    if os.path.exists(fn_daily):
        print '%s existed!'%fn_daily
        return
    maxday=0
    yyyy=int(yyyyqn[:4])
    qn=int(yyyyqn[5])
    assert qn in (1,2,3,4)
    assert yyyyqn[4]=='q'
    weekmap=['周一','周二','周三','周四','周五','周六','周日']
    ts_start=time.mktime((yyyy,(qn-1)*3+1,1,0,0,0,0,0,0))
    for i in range(31*3):
        tss=time.localtime(ts_start+86400*i)
        if tss.tm_mon>=(qn*3+1):
            break
        else:
            maxday=i+1
    #print maxday
    weeklist=[]
    oneweek=[]
    weeklist.append(oneweek)
    for day in range(1,maxday+1):
        tss=time.localtime(ts_start+86400*(day-1))
        title='%02d-%02d%s'%(tss.tm_mon,tss.tm_mday,weekmap[tss.tm_wday])
        if tss.tm_wday==0:  #周一了
            oneweek=[]
            weeklist.append(oneweek)
        oneweek.append(title)
    if not weeklist[0]:
        del weeklist[0]
    fo=open(fn_daily,'w')
    fo.write('=========\n%s\n=========\n\n'%yyyyqn)
    fo.write(':作者: gashero\n\n')
    fo.write('.. contents:: 目录\n.. sectnum::\n\n')
    fo.write('.. raw:: html\n\n')
    fo.write('    <style> .todo {color: #ffcc00} </style>\n')
    fo.write('    <style> .done {color: #66cc00} </style>\n')
    fo.write('    <style> .fail {color: #cc3300} </style>\n\n')
    fo.write('.. role:: todo\n.. role:: done\n.. role:: fail\n\n')
    for weekidx,oneweek in zip(range(len(weeklist)),weeklist):
        #print weekidx,oneweek
        fo.write('Week%d\n=======\n\n'%(weekidx+1))
        for title in oneweek:
            fo.write('%s\n-----------\n\n'%title)
    fo.close()
    return

def main():
    datadict={
            'cnt_bytes':      0,
            'cnt_chars':      0,
            'cnt_rst':        0,
            'time_now':         time.strftime('%Y-%m-%d %H:%M:%S'),
            '@page':            0,
            '@wait':            0,
            'topchars':         [],
            }
    walktree('.',datadict)
    datadict['chars/papers']='%.02f'%(
            datadict['cnt_chars']*1.0/datadict['cnt_rst'],)
    datadict['topchars'].sort(key=lambda x:x[1],reverse=True)
    for k in ('cnt_bytes','cnt_rst','cnt_chars','chars/papers',
            'time_now'):
        print '%-16s%s'%(k,datadict[k])
    if len(sys.argv)>1:
        if sys.argv[1]=='topchars':
            for (fn_full, chars) in datadict['topchars']:
                print '%-60s\t%d'%(fn_full,chars)
        elif sys.argv[1]=='bookmark':
            for k in ('@page','@wait'):
                print '%-16s%s'%(k,datadict[k])
        elif sys.argv[1]=='progress':
            fn_rst=sys.argv[2]
            progress=get_progress(fn_rst)
            print progress
        elif sys.argv[1]=='newdaily':
            newdaily(sys.argv[2])
        else:
            print 'Unknown command:',repr(sys.argv[1:])
    return

if __name__=='__main__':
    main()
