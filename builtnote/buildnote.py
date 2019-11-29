#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# File: buildnote.py
# Date: 2011-03-02
# Author: gashero

"""
将特定目录的rst文件编译成html文件存放于此。
"""

import os
import sys
import re
import hashlib
import time
import json
import subprocess

from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive
from docutils import nodes
from docutils.core import publish_string
from docutils.core import publish_parts

CURPATH=os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))
RE_MD5=re.compile(r"""([0-9a-f]{32})""")
RE_FILEINFO=re.compile(r"""<!-- fileinfo= (.*?) -->""")
RE_DOCUTILS_VERSION=re.compile(r"""<meta name="generator" .*? />""")

HTML_HEAD="""\
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<title>%(title)s</title>
<style>
<!--
td,th { border:1px solid; padding:8px;}
tr { height: 24px;}
-->
</style>
</head>
<body>
<h1>%(title)s</h1>
<table>
<tr>
<th>标题</th>
<th>大小</th>
<th>字数</th>
<th>文件数</th>
<th>文件名</th>
</tr>
"""
HTML_LINE="""\
<tr><td><a href="%(link)s">%(name)s</a></td><td>%(size)s</td><td>%(char_count)d</td><td>%(rst_count)s</td><td>%(link)s</td></tr>
"""
HTML_TAIL="""\
</table>
</body>
</html>
"""

def get_file_hash(filename):
    """使用文件计算MD5值得出哈希，比svn那个快好多，只要0.3秒
    就可以完成gsnote中603个文件的全部检查
    """
    ff=open(filename,'rU')
    data=ff.read()
    ff.close()
    mm=hashlib.md5(data)
    return mm.hexdigest(),data

def get_html_fileinfo(fn_html):
    """从html文件里提取fileinfo，避免文件冲突"""
    if not os.path.exists(fn_html):
        return {}
    fin=open(fn_html,'rU')
    data=fin.read()
    fin.close()
    mo=RE_FILEINFO.search(data)
    if mo:
        return json.loads(mo.groups()[0])
    else:
        return {}

class TravelDirTree(object):

    def __init__(self,rootpath):
        self.rootpath=os.path.normpath(rootpath)
        return

    def run(self):
        nowdir=''
        self.travel_path('')
        return

    def travel_path(self,nowdir):
        rstfile_list=[]
        dir_list=[]
        rst_bytes=0
        html_bytes=0
        char_count=0
        rst_count=0
        dflist=os.listdir(os.path.join(self.rootpath,nowdir))
        dflist.sort()
        for df in dflist:
            fullpath=os.path.join(self.rootpath,nowdir,df)
            if os.path.isfile(fullpath):
                if df.endswith('.rst'):
                    #self.do_rstfile(os.path.join(nowdir,df))
                    rstfile_list.append(df)
                elif df=='gstat.py':
                    pass
                else:
                    print 'OTHER FILE: %s'%os.path.join(nowdir,df)
            elif os.path.isdir(fullpath):
                if df not in ('.svn','.hg','.git','_images'):
                    #self.do_dir(os.path.join(nowdir,df))
                    #self.travel_path(os.path.join(nowdir,df))
                    dir_list.append(df)
                else:
                    pass
            else:
                print 'OTHER DF: %s'%os.path.join(nowdir,df)
        showlist=[]
        rst_count=len(rstfile_list)
        for df in dir_list:
            self.do_dir(os.path.join(nowdir,df))
            dirinfo=self.travel_path(os.path.join(nowdir,df))
            showlist.append({
                'name':df+'/',
                'link':df+'/index.html',
                'size':dirinfo['rst_bytes'],
                'char_count':dirinfo['char_count'],
                'rst_count':dirinfo['rst_count'],
                })
            rst_bytes+=dirinfo['rst_bytes']
            char_count+=dirinfo['char_count']
            rst_count+=dirinfo['rst_count']
        for df in rstfile_list:
            fileinfo=self.do_rstfile(os.path.join(nowdir,df))
            showlist.append({
                'name':fileinfo['title'],
                'link':df.replace('.rst','.html'),
                'size':fileinfo['src_size'],
                'char_count':fileinfo['char_count'],
                'rst_count':'',
                })
            rst_bytes+=fileinfo['src_size']
            html_bytes+=fileinfo['dst_size']
            char_count+=fileinfo['char_count']
        INDEX_FILENAME=os.path.join(nowdir,'index.html')
        ff=open(os.path.join(nowdir,'index.html'),'w')
        ff.write(HTML_HEAD%{'title':nowdir})
        for t in showlist:
            t['name']=t['name'].encode('utf-8')
            ff.write(HTML_LINE%t)
        ff.write(HTML_TAIL)
        ff.close()
        dst_filelist=os.listdir(nowdir or '.')
        for f in ['.svn','.hg','.git','_rst.css','index.html','_images',
                '_mathjax','_filehash.db','buildnote.py','epubbuild.py',
                'ui',]:
            if f in dst_filelist:
                dst_filelist.remove(f)
        dst_filelist=filter(lambda x:x not in dir_list,dst_filelist)
        dst_filelist=filter(lambda x:x not in rstfile_list,map(
            lambda y:y.replace('.html','.rst'),dst_filelist))
        dst_filelist=filter(lambda x:not x.endswith('.svg'),dst_filelist)
        if dst_filelist:
            for f in dst_filelist:
                f=f.replace('.rst','.html')
                print '[useless]',os.path.join(nowdir,f)
        return {'rst_bytes':rst_bytes,
                'html_bytes':html_bytes,
                'char_count':char_count,
                'rst_count':rst_count,}

    def do_dir(self,dirname):
        #print '[dir ]',dirname
        if not os.path.exists(dirname):
            os.mkdir(dirname)
            os.system('cp %s %s'%('_rst.css',dirname))
        elif not os.path.isdir(dirname):
            raise RuntimeError,'%s is not a dir'%dirname
        else:
            pass    #dir is exist
        return

    def do_rstfile(self,filename_rst):
        return build_rstfile(filename_rst,self.rootpath)

def build_rstfile(filename_rst,rootpath):
    """
    将rst文件的处理独立出来，方便单独编译
    实测rootpath只有一种选择，即"../gsnote"
    而filename_rst则是形如"web/chrome.rst"
    """
    fullpath=os.path.join(rootpath,filename_rst)
    filename_html=filename_rst.replace('.rst','.html')
    filehash,filedata=get_file_hash(fullpath)
    try:
        fileinfo=get_html_fileinfo(filename_html)
        if fileinfo['filehash']==filehash:
            return fileinfo
    except KeyError:
        pass
    print '[rst ]',filename_rst
    if os.path.split(filename_html)[0]:
        os.chdir(os.path.split(filename_html)[0])
    else:
        os.chdir(CURPATH)
    if filename_rst.startswith('idea/slideshow'):
        writer='s5'
    else:
        writer='html'
    rstdict=publish_parts(
            filedata,writer_name=writer,
            settings_overrides={
                'link-stylesheet':True,
                'stylesheet':'_rst.css',
                'stylesheet_path':'',
                })
    os.chdir(CURPATH)
    htmldata=rstdict['whole'].encode('utf-8')
    fileinfo={
            'filehash':filehash,
            'src_size':len(filedata),
            'dst_size':len(htmldata),
            'char_count':len(filedata.decode('utf-8')),
            'title':rstdict['title'],
            }
    ff=open(filename_html,'w')
    savedata=htmldata.replace(
        'http://cdn.mathjax.org/mathjax/latest/MathJax.js',
        '/'.join(['..']*filename_html.count('/'))+'/_mathjax/MathJax.js',
        )
    savedata=RE_DOCUTILS_VERSION.sub('',savedata,1)
    savedata+='<!-- fileinfo= %s -->\n'%json.dumps(fileinfo)
    ff.write(savedata)
    ff.close()
    return fileinfo

#XXX: 内嵌dot的支持
FORMAT_OPTIONS={
        #'neato':['-Gmaxiter=1000','-Goverlap=false','-Esplines=true','-Gsep=0.1',],
        'neato':['-Gmaxiter=10000','-Goverlap=false','-Esplines=true','-Gsep=-0.10',],
        }
class Dot(Directive):
    has_content=True
    option_spec={
            'layout':lambda arg:directives.choice(arg,('dot','neato',
                'twopi','circo','fdp')),
            'format':lambda arg:directives.choice(arg,('png','svg')),
            'filename':directives.unchanged,
            }

    def run(self):
        self.options.setdefault('layout','neato')
        self.options.setdefault('format','png')
        content=u'\n'.join(self.content)
        other_options=FORMAT_OPTIONS.get(self.options['layout'],[])
        p=subprocess.Popen([self.options['layout'],'-T'+
            self.options['format']]+other_options,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        p.stdin.write(content.encode('utf-8'))
        p.stdin.close()
        datalines=p.stdout.readlines()
        del datalines[:3]
        #ff=open(self.options['filename'],'w')
        #ff.write(data)
        #ff.close()
        #return [nodes.raw('',"""<embed src="%s" />"""%\
        #        self.options['filename'],format='html')]
        return [nodes.raw('',''.join(datalines).decode('utf-8'),format='html')]
directives.register_directive('dot',Dot)

#XXX: 内嵌SVG的支持
#class SVG(Directive):
#    has_content=True
#    option_spec={
#            'filename': directives.unchanged_required,
#            'height':   directives.unchanged_required,
#            'width':    directives.unchanged_required,
#            }
#
#    def run(self):
#        content=u'\n'.join(self.content)
#        filename=self.options['filename']
#        height=self.options.get('height',200)
#        width=self.options.get('width',200)
#        fo=open(filename,'w')
#        fo.write('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'''+
#            '''<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n'''+
#            '''"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n'''+
#            '''<svg xmlns="http://www.w3.org/2000/svg" height="%s" width="%s">\n'''%(height,width))
#        fo.write(content)
#        fo.write('''</svg>\n''')
#        fo.close()
#        return [nodes.raw('',"""<embed src="%s" type="image/svg+xml" />"""%\
#                filename,format='html')]

class SVG(Directive):
    has_content=True
    option_spec={
            'height':   directives.unchanged_required,
            'width':    directives.unchanged_required,
            }

    def run(self):
        contentlist=[u'\n'.join(self.content),]
        height=self.options.get('height',600)
        width=self.options.get('width',600)
        contentlist.insert(0,u'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="%s" height="%s">'%(width,height))
        contentlist.append(u'</svg>')
        return [nodes.raw('','\n'.join(contentlist)+'\n',format='html')]
directives.register_directive('svg',SVG)

class PillowDraw(Directive):
    has_content=True
    option_spec={
            'filename':     directives.unchanged_required,
            'height':       directives.unchanged_required,
            'width':        directives.unchanged_required,
            }

    def run(self):
        #print repr(self.content)
        from PIL import Image
        from PIL import ImageDraw
        filename=self.options['filename']
        width=int(self.options['width'])
        height=int(self.options['height'])
        image=Image.new('RGBA',(width,height),(0,0,0,0))
        draw=ImageDraw.Draw(image)
        exec '\n'.join(self.content)
        image.save('_images/%s'%filename)
        htmlimage='<img src="_images/%s" />\n'%filename
        return [nodes.raw('',htmlimage,format='html')]

directives.register_directive('pillow',PillowDraw)

def main():
    time_start=time.time()
    if len(sys.argv)==1:
        tdt=TravelDirTree('../gsnote')
        #print tdt.rootpath
        try:
            tdt.run()
        except KeyboardInterrupt:
            print
    else:
        fn=sys.argv[1]
        if os.path.exists(fn):
            if os.path.isfile(fn):
                fn=fn.replace('.html','.rst')
                build_rstfile(fn,'../gsnote')
            elif os.path.isdir(fn):
                dn=fn
                for df in os.listdir(dn):
                    if df=='index.html':
                        continue
                    fn=os.path.join(dn,df)
                    if fn.endswith('.html') and os.path.isfile(fn):
                        fn=fn.replace('.html','.rst')
                        build_rstfile(fn,'../gsnote')
                    else:
                        continue
            else:
                raise RuntimeError('%s not dir or file.'%fn)
        else:
            raise RuntimeError('%s not exist'%fn)
    time_stop=time.time()
    print 'Time spend: %.03f'%(time_stop-time_start)
    return

if __name__=='__main__':
    main()
