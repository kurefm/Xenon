# 开发说明

### 目录及文件
#### packages目录
存放系统使用的第三方非二进制库，减少部署中安装库的麻烦。但由于二进制库需要针对不同平台编译，只能在部署时再安装。

要想使用packages目录下的库，在import时在要导入的库名前添加：
```Python
packages.
```
即可。

比如要导入rsa库，正常情况下使用如下语句导入：
```Python
import rsa
```
在这里，你需要使用：
```Python
import packages.rsa
```

#### test目录
test目录存放测试中的代码，要添加不确定的代码请先在此目录下进行测试。请务必保crawler、data、analysis这3个项目目录的整洁和可用，不要盲目地向其中添加不可靠的代码。 

#### cookies目录
用于存放会话中用的cookie，以账号为文件名进行存储，保存为Mozilla格式。由crawler中的cookielib自动进行管理。为了避免账号泄露，.cookie文件不会同步到git上。  

#### crawler.py文件
爬虫的最终实现文件，提供一系列的接口来创建、使用和管理爬虫。  

#### data.py文件
数据中心的最终实现文件，提供一系列存储和读取数据的接口。  

#### analysis.py文件
数据分析的最终实现文件，提供一系列数据分析的方法。  

#### common.py文件
提供系统中通用的类和函数，主要包括全局配置文件读写，全局日志记录。  

#### errors.py文件
提供系统中用到的所有自定义异常。  

#### models.py文件
提供系统中使用数据模型。  

#### xenon.py文件
Xenon系统的启动文件，用于管理整个系统，预计提供命令行管理模式和Web管理模式。  

#### config文件
该文件将用于系统的全局配置。  


### 未提及的文件和目录
- 一般情况下不再考虑增加目录。  
- 如果开发过程中需要构建的中间模块，直接在src根目录下添加文件即可。  
###.gitignore忽略
- src目录中的所有Python二进制文件，包括.pyc,.pyo,.pyd。  
- 以及PyChram的工程目录.idea。  
- cookies文件夹下的.cookie文件。  
- 账号列表文件accounts。  

### 代码编写规范
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
在Pycharm中快速插入该格式注释的方法是在函数的下一行输入三个双引号（半角）"，再按回车，即可自动识别函数的参数并建立格式的注释。  
