================
gsnote笔记系统
================

:作者: gashero
:日期: 2019-11-29
:地址: https://github.com/gashero/gsnote

.. contents:: 目录
.. sectnum::

简介
======

本文档记录gsnote笔记系统的使用，按章节开源到 https://github.com/gashero/gsnote/wiki 。

基础功能
==========

gsnote是什么
--------------

gsnote是一套个人笔记管理系统，用于更好的管理个人笔记，其中一些功能可以对记录笔记的行为形成正向激励，使得自己的个人知识库更加完善。

主要功能特性：

#. 基于reStructuredText文本标记语言
#. 完善的统计功能，使得自己的笔记可以更好的量化
#. 特定目录用于每日记录
#. 支持特定目录编译为s5演讲稿
#. 支持graphviz内嵌代码并转换为html内嵌SVG图
#. 支持内嵌SVG代码转换为html内嵌SVG图
#. 支持Python Pillow库代码生成图片
#. 支持数学公式，基于mathjax库
#. 整个编译出的笔记可以完全离线工作，包括数学公式在内只需引用本地文件而无需访问网络

目录
------

gsnote早期是个人笔记工具，过程中有些硬编码的目录。笔记的源码需放在 ``gsnote`` 目录中，笔记编译生成html文件需放在 ``builtnote`` 目录中。 ``gsnote`` 目录和 ``builtnote`` 目录应该放在同一目录下。

每一篇笔记所引用的图片，需放在buildnote目录下，对应笔记所在目录的 ``_images`` 目录内，文件名应该尽量保持与笔记名字相同加后缀的方式方便管理。避免不同笔记引用相同的图片。

脚本 ``gstat.py`` 应该放在 ``gsnote/`` 目录内，主要用于笔记的统计，以及若干警告。脚本 ``buildnote.py`` 应该放在 ``builtnote/`` 目录内，用于构建笔记。

构建
------

要将笔记源码构建生成html文件，只需要切换进入 ``builtnote/`` 目录，然后执行::

    ./buildnote.py

就会将整个笔记源码目录扫描，找到有更新的笔记进行编译。并生成整体目录结构和索引。通常只有几篇笔记有更新时，构建时间低于1秒，所以推荐使用。

如果需要编译特定的笔记，也可以将笔记的html文件名传入作为参数，这样运行速度更快::

    ./buildnote.py hello/world.html

构建完成后在 ``builtnote/index.html`` 可以作为个人笔记系统的入口。即可以直接用浏览器访问，点击进入查看每一篇笔记，也可以用http服务器来供内网分享，一个简单的http服务器可以在切换到 ``builtnote/`` 目录后执行::

    python -m SimpleHTTPServer

这样就可以在其他机器上使用浏览器访问ip:port的方式来查看自己的整个笔记系统了。

reStructuredText
------------------

reStructuredText，简称rest，是一种文本标记语言，通过特定格式的纯文本来定义文本内容的格式和含义。这样生成的笔记，对vim一类的编辑器是默认带有语法高亮支持的，使得即便是不通过浏览器而仅仅用vim编辑器也能比较好的浏览笔记系统。这在没有图形GUI的环境里，比如服务器上，也能很好的使用。

rest最初是 docutils_ 项目的一部分。

.. _docutils: http://docutils.sourceforge.net/

rest的入门可以参考 `A ReStructuredText Primer`_ 。

.. _`A RestructuredText Primer`: http://docutils.sourceforge.net/docs/user/rst/quickstart.html

最简单而常用的几个格式就可以覆盖大多数需求了。

笔记的标题::

    =============
    笔记的标题
    =============

自动生成章节编号和目录::

    .. contents:: 目录
    .. sectnum::

一级标题、二级标题、三级标题::

    一级标题
    ==========

    二级标题
    ----------

    三级标题
    ~~~~~~~~~~

引用图片::

    .. image:: _images/python.png

其他略常用的也就是表格、链接、块引用几个，尽管文档看起来稍大，但用起来其实很简单。

快速入门
----------

建立一个git版本库，比如叫做mynote。将本项目的所有内容复制到mynote里，必要的脚本如 ``mynote/gsnote/gstat.py`` 和 ``mynote/builtnote/buildnote.py`` 。

进入 ``mynote/gsnote/`` 目录里开始用rest编写笔记，注意扩展名为 ".rst" 。

进入 ``mynote/builtnote/`` 目录构建笔记，执行 ``./buildnote.py`` 。

用浏览器打开 ``mynote/builtnote/index.html`` ，浏览自己的笔记。

使用规范
==========

额外的限制
------------

``gstat.py`` 脚本为防止琐碎笔记等做了很多额外的限制，使得笔记不符合规范时会有警告：

#. 当前支持的笔记要求扩展名必须为".rst"， ``gsnote/`` 里的其他文件会导致"unknown file"报警
#. 笔记中的引用的图片必须放在正确的位置，否则会提示"LostImage"，并给出笔记文件名和图片文件名
#. 笔记源文件应该使用 ``\n`` 换行，如果笔记内容里有 ``\r`` ，会提示"DOSFILE"报警
#. 笔记应该使用UTF-8编码，如果有有解码错误，会提示"GBKFILE"报警
#. 笔记中空格数量不应过多，当空格比例超过1/2.8时，会提示"MANY BLANK"
#. 笔记的字数不应少于1000个unicode字符，否则会提示"SMALLFILE"

自动避免重复编译
------------------

``buildnote.py`` 脚本会自动在编译出的html文件里用HTML注释存储源文件的MD5。

这样在每次进行笔记构建时，会自动检查每个源文件与html文件里的MD5是否相同。不同的才会编译。

该功能使得构建一个拥有数千个源文件的大型笔记系统里的几个文件修改时，也能在少于1秒内完成。

图片目录规范
--------------

图片是被html所引用的，所以应该放在广义的 ``builtnote/`` 目录下。构建过程不会移动和修改图片。

例如一个笔记的文件名是 ``mynote/category1/note1.rst`` ，其内使用了图片指令 ``.. image:: _images/hello.png`` ，那么图片应该放在 ``mynote/builtnote/category1/_images/hello.png`` 。

图片的命名没有做限制，建议实际图片文件名使用笔记的名字作为前缀。

笔记统计功能
==============

笔记统计
----------

不带参数执行 ``gsnote.py`` 即可显示笔记统计。详尽的统计有助于促进自己多学习和记录::

    $ ./gstat.py 
    cnt_bytes       22360666
    cnt_rst         1515
    cnt_chars       13405272
    chars/papers    8848.36
    time_now        2020-10-12 14:26:31

各个字段的解释：

#. cnt_bytes：以字节计的笔记总量，只会记录reStructuredText格式的
#. cnt_rst：reStructuredText格式的笔记篇数，即.rst文件数量
#. cnt_chars：所有笔记的字符数，是以所有笔记解码为Unicode后统计的Unicode字符数
#. chars/papers：平均每篇笔记的字符数
#. time_now：此次统计时间

书籍笔记进度统计
------------------

所有的笔记均可使用 ``@page <page1>-<page2>`` 形式来记录哪些还没学习的部分。通过这些标签可以统计出书籍笔记的阅读进度。参数为 progress 和笔记文件名，例如::

    $ ./gstat.py progress ml/book_深度学习入门_基于Python的理论与实现.rst 
    cnt_bytes       22361349
    cnt_rst         1515
    cnt_chars       13405713
    chars/papers    8848.66
    time_now        2020-10-12 14:29:04
    {'maxpage': 278, 'cnt_bookmark': 33, 'unread': 216}

最后一行的dict里字段解释：

#. maxpage：根据 `@page` 书签记录的最大页码，可以当作书籍总页数
#. cnt_bookmarks： `@page` 书签数量
#. unread：未读的页数，每个 `@page` 里page2-page1得到的数字的累计

顶级笔记统计
--------------

使用 `topchars` 参数，可以统计那些字数在5万字以上的笔记，用以统计和激励自己的学习。例如::

    $ ./gstat.py topchars
    cnt_bytes       22362189
    cnt_rst         1515
    cnt_chars       13406271
    chars/papers    8849.02
    time_now        2020-10-12 14:32:49
    ./python/book_Python2.1宝典.rst                           	211992
    ./computer/erlang/book_Programming_Erlang_En.rst            	167255
    ./computer/java/book_Java2教程_第五版.rst              	130186
    ./computer/lua/book_Lua程序设计_2nd.rst                 	114107
    ./linux/book_Linux应用程序开发_2nd.rst                	99435
    ./python/twisted/book_Twisted网络编程必备.rst         	94535
    ./multimedia/vision/article_opencv_python_tutorial.rst      	91440
    ./linux/book_Linux下的C编程.rst                         	85533

每一行是笔记文件名和字数。

完成笔记统计
--------------

书籍类的笔记，如果记录完成，可以在最后加上标签 `@done` 。随后就可以统计出来这些完成的书籍笔记。例如::

    $ ./gstat.py bookdone
    cnt_bytes       22363143
    cnt_rst         1515
    cnt_chars       13407059
    chars/papers    8849.54
    time_now        2020-10-12 14:34:18
    ./arm/book_armcortexm3外围接口电路与工程实践基础应用.rst
    ./aviation/aircraft/book_无人机DIY.rst
    ./aviation/aircraft/book_无人机_引领空中机器人新革命.rst
    ./business/quant/book_高频交易之战.rst
    ./business/startup/book_创业的国度.rst
    ./computer/java/book_Java2教程_第五版.rst
    ./computer/lua/book_Lua程序设计_2nd.rst

日志、演讲稿
==============

daily功能
-----------

.. todo

s5演讲稿
----------

.. todo

版本库、同步建议
==================

版本库管理
------------

.. todo 如何自己搭建版本库

多设备同步
------------

.. todo 手机应用，浏览器固定页

绘图功能
==========

graphviz流程图
----------------

.. todo

内嵌SVG图
-----------

.. todo

PIL函数绘图
-------------

.. todo

数学公式
==========

数学公式实现方案
------------------

.. todo

MathJax入门使用
-----------------

.. todo

FAQ
=====

已知的小bug
-------------

对新建目录的编译，可能会提示"_rst.css"找不到，可以自行将 ``mynote/builtnote/_rst.css`` 拷贝到新目录即可。

newdaily命令生成的日期可能会多一天。
