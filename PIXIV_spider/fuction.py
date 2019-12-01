import re, requests, time
from urllib.parse import urlencode

'''
            主要的函数都在这个文件内
'''
# 公用头文件
head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
}


def set_leaderboard(content: str, mode: str, R18: bool, date: str) -> list:
    """
    选择进入的排行榜
    不是所有分区都有所有的排行榜模式，如动图区只有今日和本周两个模式
    建议去P站确定各参数后再调用
    :param content: 排行榜的分区，包括综合、插画、动图、漫画
    :param mode: 排行榜的模式，包括今日、本周、新人、受男性欢迎、受女性欢迎
    :param R18: 是否进入R18模式
    :param date: 排行榜具体时间
    :return: 排行榜参数列表，可用在其他函数中
    """

    print("已设置起始榜单为" + date[:4] + "年" + date[4:6] + "月" + date[6:8] + "日" + content + "区" + mode + "榜")

    if content == '综合':
        content = ''
    elif content == '插画':
        content = 'illust'
    elif content == '动图':
        content = 'ugoira'
    elif content == "漫画":
        content = 'manga'

    if mode == '今日':
        mode = 'daily'
    elif mode == '本周':
        mode = 'weekly'
    elif mode == '本月':
        mode = 'monthly'
    elif mode == '新人':
        mode = 'rookie'
    elif mode == '受男性欢迎':
        mode = 'male'
    elif mode == '受女性欢迎':
        mode = 'female'

    if R18:
        mode = mode + '_r18'
    else:
        mode = mode + ''

    return [content, mode, date]


def __login(username: str, password: str) -> requests.sessions.Session:
    """
    登陆函数
    :param username: 用户名
    :param password: 密码
    :return: 该用户名的会话(session)
    """
    # 模拟一下浏览器
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

    # 用requests的session模块记录登录的cookie

    session = requests.session()

    # 首先进入登录页获取post_key，我用的是正则表达式
    response = session.get('https://accounts.pixiv.net/login?lang=zh')
    post_key = re.findall('<input type="hidden" name="post_key" value=".*?">',
                          response.text)[0]
    post_key = re.findall('value=".*?"', post_key)[0]
    post_key = re.sub('value="', '', post_key)
    post_key = re.sub('"', '', post_key)

    # 将传入的参数用字典的形式表示出来，return_to可以去掉
    data = {
        'pixiv_id': username,
        'password': password,
        'return_to': 'https://www.pixiv.net/',
        'post_key': post_key,
    }

    # 将data post给登录页面，完成登录
    session.post("https://accounts.pixiv.net/login?lang=zh", data=data, headers=head)
    return session


def load_leaderboard(username: str, password: str, set_leaderboard: list) -> list:
    """
    进入榜单
    :param username: 用户名
    :param password: 密码
    :param set_leaderboard: 榜单参数
    :return: 带有图片url等信息的字典组成的列表
    """
    # 使用前确保set_leaderboard()函数已调用，并将其返回的参数列表传入该函数
    response_list = []

    # 先登录用户
    session = __login(username, password)

    # 初始化爬取的页数以及所需传入的参数
    p = 1
    data = {
        'mode': set_leaderboard[1],  # 这些是 set_leaderboard()函数返回的参数
        'content': set_leaderboard[0],
        'date': set_leaderboard[2],
        'p': p,
        'format': 'json'
    }
    print("正在加载" + "https://www.pixiv.net/ranking.php?" + urlencode(data))

    # 如果date是今天，需要去除date项;如果content为综合，需要去除content项。
    # 这是因为P站排行榜的今日榜不需要传入'date'，而综合区不需要传入'content'
    if set_leaderboard[2] == time.strftime("%Y%m%d"):
        data.pop('date')
    if set_leaderboard[0] == '':
        data.pop('content')

    # 开启循环进行翻页
    while True:

        # 翻页并更新data中的'p'参数
        data['p'] = p
        p = p + 1

        # 使用urlencode()函数将data传入url，获取目标文件
        url = "https://www.pixiv.net/ranking.php?" + urlencode(data)
        response = session.get(url)

        # 处理的到的文件并转为字典形式
        # 不加以下这些会报错，似乎是因为eval()不能处理布尔型数据
        global false, null, true
        false = 'False'
        null = 'None'
        true = 'True'
        try:
            response = eval(response.content)['contents']
        except KeyError:
            break
        response_list = response_list + response

    # 返回一个列表，列表元素为字典形式，包括了图片的各个信息
    return response_list


def leaderboard_turn_next_page(set_leaderboard: list) -> list:
    """
    排行榜前一天
    :param set_leaderboard: 排行榜参数列表，来自于set_leaderboard()函数
    :return: 前一天排行榜的参数列表
    """
    date = int(set_leaderboard[2])
    date = date - 1
    set_leaderboard[2] = date
    return set_leaderboard  # 返回的是一个列表


def leaderboard_turn_previous_page(set_leaderboard: list) -> list:
    """
    排行榜后一天
    :param set_leaderboard: 排行榜参数列表，来自于set_leaderboard()函数
    :return: 后一天排行榜的参数列表
    """
    date = int(set_leaderboard[2])
    date = date + 1
    set_leaderboard[2] = date
    return set_leaderboard


def get_author_id(response_list: list) -> list:
    """
    得到作者的ID
    :param response_list: 响应列表，来自于load_leaderboard()函数
    :return: 排行榜内作者ID组成的列表
    """
    author_id_list = []
    for element in response_list:
        author_id_list.append(str(element['user_id']))
    return author_id_list


def get_author_img_dic(author_id: str, username: str, password: str) -> dict:
    """
    获取作者的全部作品字典
    :param author_id: 作者ID
    :param username: 用户名
    :param password: 密码
    :return: 作者的全部作品字典
    """
    # 登录用户
    session = __login(username, password)
    response = session.get('https://www.pixiv.net/ajax/user/' + author_id + '/profile/all')

    # 不加以下这些会报错，似乎是因为eval()不能处理布尔型数据
    global false, null, true
    false = 'False'
    null = 'None'
    true = 'True'
    author_img_dic = eval(response.content)['body']
    print(author_img_dic)

    return author_img_dic


def get_author_illusts(author_img_dic: dict) -> list:
    """
    获得作者的插画与动图ID
    :param author_img_dic: 作者的全部作品字典，来自于get_author_img_dic()函数
    :return: 作者的插画与动图ID列表
    """
    author_illusts_dic = author_img_dic['illusts']
    illusts_list = [key for key, value in author_illusts_dic.items()]
    return illusts_list


def get_author_manga(author_img_dic: dict) -> list:
    """
    获得作者的漫画ID
    :param author_img_dic: 作者的全部作品字典，来自于get_author_img_dic()函数
    :return: 作者的漫画ID列表
    """
    author_manga_dic = author_img_dic['manga']
    manga_list = [key for key, value in author_manga_dic.items()]
    return manga_list


def get_author_mangaSeries(author_img_dic: dict) -> list:
    """
    获取作者的漫画系列ID
    :param author_img_dic: 作者的全部作品字典，来自于get_author_img_dic()函数
    :return: 作者的漫画系列ID列表
    """
    author_mangaSeries_dic = author_img_dic['mangaSeries']
    mangaSeries_list = [key for key, value in author_mangaSeries_dic.items()]
    return mangaSeries_list


def get_img_dic(img_id: str, username: str, password: str) -> dict:  # 传入图片ID，返回该图片ID下的信息，具体信息见注释
    """
    获得某个图片ID下的信息，具体信息见注释
    :param img_id: 图片ID
    :param username: 用户名
    :param password: 密码
    :return: 图片ID下的信息字典
    """
    '''
    图片ID下的信息字典
    img_dic = {
        'illustID' : 插画ID
        'illustTitle' : 插画标题
        'illustDescription' : 插画简介
        'createDate' : 插画创建时间
        'uploadDate' : 插画更新时间
        'tags' : 插画tag,值为列表
        'authorID' : 作者ID
        'authorName' : 作者昵称
        'imgUrl' : 插画原始大小url,值为列表
    }
    '''
    img_dic = {}
    # 登录用户
    session = __login(username, password)

    # 获取第一个文件的信息，把除了图片url以外的东西先拿到
    url_1 = 'https://www.pixiv.net/ajax/illust/' + img_id
    response_1 = session.get(url_1)
    # 不加以下这些会报错，似乎是因为eval()不能处理布尔型数据
    global false, null, true
    false = 'False'
    null = 'None'
    true = 'True'
    response_1 = eval(response_1.content)['body']
    img_dic['illustID'] = response_1['illustId']  # 图片ID
    img_dic['illustTitle'] = response_1['illustTitle']  # 图片标题
    img_dic['illustDescription'] = response_1['illustComment']  # 图片简介
    img_dic['createDate'] = response_1['createDate']  # 创建时间
    img_dic['uploadDate'] = response_1['uploadDate']  # 更新时间
    img_dic['tags'] = []  # 因为有多个tag，所以'tags'的值用列表形式保存
    for tag in response_1['tags']['tags']:
        img_dic['tags'].append(tag['tag'])
    img_dic['authorID'] = response_1['tags']['tags'][0]['userId']
    img_dic['authorName'] = response_1['tags']['tags'][0]['userName']

    # 获取第二个文件的信息，把图片url拿到
    url_2 = 'https://www.pixiv.net/ajax/illust/' + img_id + '/pages'
    response_2 = session.get(url_2)
    response_2 = eval(response_2.content)['body']
    img_dic['imgUrl'] = []  # 因为存在好几个插画在同一页面的情况，所以'imgUrl'的值用列表形式保存
    for img_url in response_2:
        img_dic['imgUrl'].append(img_url['urls']['original'].replace('\\', ''))

    return img_dic


def get_img_imformation(img_dic: dict) -> dict:
    """
    提取下载图片所需的信息
    :param img_dic:
    :return: 图片ID下的信息字典，来自get_img_dic()函数
    """
    img_imformation = {}
    img_imformation['img_url'] = img_dic['imgUrl']
    img_imformation['img_id'] = img_dic['illustID']
    img_imformation['img_title'] = img_dic['illustTitle']
    return img_imformation


# 这些是未完成函数，大概是通过搜索获取图片信息的函数
# def set_search(word, s_mode, mode, order, scd, ecd, type, p):
#     data = {
#         'word': word,
#         's_mode': s_mode,
#         'mode': mode,
#         'order': order,
#         'scd': scd,
#         'ecd': ecd,
#         'type': type,
#         'p': p
#     }
#
#     if scd == '' or ecd == '':
#         data.pop('scd')
#         data.pop('ecd')
#     if type == '':
#         data.pop('type')
#
#     return data
#
#
# def load_search(username, password):
#     session = __login(username, password)
#     a = session.get('https://www.pixiv.net/search.php?s_mode=s_tag&word=%E7%B4%94%E6%84%9B%E3%82%B3%E3%83%B3%E3%83%93')
#     print(a.content)


def download(img_imformation: dict, address: str):  # 下载图片，以图片标题命名
    """
    下载图片，以图片标题命名
    :param img_imformation: 图片下载所需信息，来自get_img_imformation()函数
    :param address: 图片保存地址
    """
    n = 0
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Referer': 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + img_imformation['img_id']
    }
    for img_url in img_imformation['img_url']:
        img_response = requests.get(img_url, headers=head)
        image = img_response.content
        try:
            if n == 0:
                with open(address + '/' + img_imformation['img_title']
                          + '.jpg', 'wb') as jpg:
                    jpg.write(image)
            else:
                with open(address + '/' + img_imformation['img_title']
                          + '(' + str(n) + ')' + '.jpg', 'wb') as jpg:
                    jpg.write(image)
        except IOError:
            print("IO Error\n")
        finally:
            jpg.close
        n = n + 1
