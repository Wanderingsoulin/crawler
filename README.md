# crawler
由于学术研究需要，写的一个爬取抖音视频的小项目。仅供研究和学习使用，商用后果自负。

环境为python 3.11，依赖包参照[environment.txt](environment.txt)中的版本，  
使用pip install xxx -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple 进行下载  
下载后修改config中的[headers_config.py](config%2Fheaders_config.py)中的cookie，即可完成基本配置

/get目录下为各运行文件，功能如下：
getByName：根据关键字搜索相关视频进行爬取  
getByUser：根据短视频作者的url爬取  
getDefault：爬取默认推荐页的视频  
getOne：测试用例，爬取一个特定url的视频  
getComment：根据输入的url，提取到下方的用户评论

/其他目录功能如下：
/video：下载的所有视频的路径  
/config/header_config：填入自己的cookie才可运行代码  
/response：开发时获取的response的相关内容，可以忽略  
/utils：工具类，供调用  
/data：用于存放获取到的评论等非视频文本数据