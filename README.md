#Xenon

![Xenon ico](xenon.png)

一个基于微博的舆情分析系统，通过爬虫抓取微博，再经过分析，从而达到预测和监控舆论的目的。

###项目名称
项目名称Xenon，来源于元素周期表的惰性元素氙(Xe)。至于为什么要用这个名称，因为我喜欢。

###项目结构
考虑代码和文档都有联合完成，于是分了doc和src目录

####doc目录
里面存放交流的文档，请使用md文件。

####src目录
本系统分为3个部分，分别是爬虫、数据中心、分析引擎，分别对应的文件夹是crawler、data、analysis。不推荐在这些文件夹下在建立文件夹。
3rd用于存放第三方的Python库，要在项目中使用第三方库，请将库的完整文件夹放入3rd中。为了保证系统的易移植，请减少二进制库的使用。
test目录存放测试中的代码，要添加不确定的代码请先在此目录下进行测试。请务必保crawler、data、analysis这3个项目目录的整洁和可用，不要盲目地向其中添加不可靠的代码。

###如何在项目中引用位于3rd中的第三方库
在你文件的import部分的最上端添加以下代码：
```Python
import sys
sys.path.append('../3rd/')
```
然后在下方按照以前的方法导入即可。

###代码编写规范
请参考Google's Python 风格指南：

- [中文版](http://zh-google-styleguide.readthedocs.org/en/latest/google-python-styleguide/ 'http://zh-google-styleguide.readthedocs.org/en/latest/google-python-styleguide/')
- [英文原版](http://google-styleguide.googlecode.com/svn/trunk/pyguide.html 'http://google-styleguide.googlecode.com/svn/trunk/pyguide.html')

特别注意变量、常量、类、方法和函数的命名。函数的注释请使用如下所示的注释格式（可以被pydoc识别）：
```Python
def get(self, url, params={}, headers={}):
    """
    Use get method to request page
    :param url:witch url do you want to request
    :param params:append params in request
    :param headers:append headers in request
    :return:it with return a response object
    """
```
在Pycharm中快速插入该格式注释的方法是在函数的下一行输入三个双引号（半角）"，在按回车，即可自动识别函数的参数并建立格式的注释。
