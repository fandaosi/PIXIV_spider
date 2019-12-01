"""
以下为下载排行榜上所有图片的作者ID的demo
"""
from fuction import set_leaderboard,load_leaderboard,\
                    leaderboard_turn_next_page,get_author_id

if __name__ == '__main__':
    set = set_leaderboard('插画', '今日', False, '20190729') #设置起始页
    response_list = load_leaderboard('用户名', '密码', set)
    id_list = get_author_id(response_list)
    page = 1
    while page <= 0:  #获得（）天的数据，获得几天就填几，如果填2就是今天与昨天
        set = leaderboard_turn_next_page(set) #前一天，也可以改成后一天，不过起始页就得改了
        response_list = load_leaderboard('用户名', '密码', set)
        id_list = id_list + get_author_id(response_list)
        id_list = list({}.fromkeys(id_list).keys()) #列表去重，合并一次去一次重
        page = page + 1
    print(id_list)
    file = open('保存地址//author_id.txt', 'w',encoding='utf-8')
    for id in id_list:
        file.write(id+'\n')
    file.close()


