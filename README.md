## clawler

由于学术研究需要，写的一个爬取抖音视频的小项目。仅供研究和学习使用，商用后果自负。

## 环境要求

- Python版本：3.11
- 依赖包版本请参照[environment.txt](environment.txt)
- 使用如下命令进行依赖安装（推荐使用清华源加快下载速度）：

  ```
  pip install xxx -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
  ```

## 基本配置

下载并安装好依赖后，请修改`config`目录下的[headers_config.py](config%2Fheaders_config.py)文件中的cookie值以完成基本配置。

## 功能模块

### /get 目录

- **getByName**：根据关键字搜索相关视频进行爬取。
- **getByUser**：根据短视频作者的url爬取其发布的视频。
- **getDefault**：爬取默认推荐页的视频。
- **getOne**：测试用例，用于爬取一个特定URL的视频。
- **getComment**：根据输入的url提取下方用户评论。
- **getCommentsByName**:【开发中】

### 其他目录说明

- **/video**：存放所有下载的视频。
- **/config/header_config**：需要填入自己的cookie才能运行代码。
- **/response**：开发过程中获取的response相关内容，可以忽略。
- **/utils**：工具类库，供其他模块调用。
- **/data**：存放获取到的评论等非视频文本数据。

如有任何问题或建议，欢迎在Issues中提出交流！

