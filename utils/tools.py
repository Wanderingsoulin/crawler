from datetime import datetime
# 对乱码 json 提取其中的关键字
def extract_aweme_ids(response_text):
    """
    暴力匹配法提取所有 aweme_id
    直接通过特征字符串定位，不依赖JSON解析
    适用于处理含乱码/不完整JSON的响应
    """
    target_pattern = '"aweme_info":{"aweme_id":"'
    ids = []
    search_pos = 0

    while True:
        # 定位关键特征字符串
        start = response_text.find(target_pattern, search_pos)
        if start == -1:
            break

        # 计算ID起始位置
        id_start = start + len(target_pattern)

        # 查找ID结束位置（下一个未转义的"）
        end = id_start
        while end < len(response_text):
            if response_text[end] == '"':
                # 检查是否被转义（前面有奇数次\）
                backslash_count = 0
                check_pos = end - 1
                while check_pos >= id_start and response_text[check_pos] == '\\':
                    backslash_count += 1
                    check_pos -= 1

                # 只有偶数次转义才认为是真正的结束符
                if backslash_count % 2 == 0:
                    break
            end += 1

        # 提取ID并验证格式（纯数字且长度>=18）
        aweme_id = response_text[id_start:end]
        if aweme_id.isdigit() and len(aweme_id) >= 18:
            ids.append(aweme_id)

        # 更新搜索位置
        search_pos = end + 1

    return ids


# 使用 name 获取数据时，命令行提示
def get_by_name_input():
    # 输入关键字，确保不为空
    while True:
        find_keyword = input("请输入查找关键字（不能为空）：").strip()
        if find_keyword:
            break
        else:
            print("关键字不能为空，请重新输入！")

    # 输入查找页数，确保为1到20之间的整数
    while True:
        try:
            pages = int(input("请输入查找页数（1到20之间的整数）："))
            if 1 <= pages <= 20:
                break
            else:
                print("页数必须在1到20之间，请重新输入！")
        except ValueError:
            print("输入无效，请输入一个整数！")
    print(f"查找关键字是：{find_keyword}，查找页数是：{pages}")
    return find_keyword, pages


# 使用 url 获取数据时，命令行提示
def get_by_url_input():
    # 输入关键字，确保不为空
    while True:
        find_url = input("请输入查找视频链接（不能为空）：").strip()
        if find_url:
            break
        else:
            print("视频链接不能为空，请重新输入！")

    # 输入查找页数，确保为1到10之间的整数
    while True:
        try:
            find_pages = int(input("请输入查找页数（1到10之间的整数）："))
            if 1 <= find_pages <= 10:
                break
            else:
                print("页数必须在1到10之间，请重新输入！")
        except ValueError:
            print("输入无效，请输入一个整数！")
    print(f"查找视频链接是：{find_url}，查找页数是：{find_pages}")
    return find_url, find_pages


# 使用 url 获取数据时，命令行提示
def get_comments_by_name_input():
    # 输入关键字，确保不为空
    while True:
        find_keyword = input("请输入查找关键字（不能为空）：").strip()
        if find_keyword:
            break
        else:
            print("关键字不能为空，请重新输入！")

    # 输入查找视频页数，确保为1到10之间的整数
    while True:
        try:
            find_video_pages = int(input("请输入查找的视频页数（1到10之间的整数）："))
            if 1 <= find_video_pages <= 10:
                break
            else:
                print("视频页数必须在1到10之间，请重新输入！")
        except ValueError:
            print("输入无效，请输入一个整数！")

    # 输入查找评论页数，确保为1到10之间的整数
    while True:
        try:
            find_comments_pages = int(input("请输入查找的评论页数（1到10之间的整数）："))
            if 1 <= find_comments_pages <= 10:
                break
            else:
                print("评论页数必须在1到10之间，请重新输入！")
        except ValueError:
            print("输入无效，请输入一个整数！")
    print(f"查找关键字是：{find_keyword}，查找视频页数是：{find_video_pages}，查找评论页数是：{find_comments_pages}")
    return find_keyword, find_video_pages, find_comments_pages

# 获取当前日期或时间，并以指定格式返回
def get_current_date(format="%Y-%m-%d"):
    # 获取当前时间
    current_time = datetime.now()

    # 格式化时间
    formatted_time = current_time.strftime(format)

    return formatted_time
