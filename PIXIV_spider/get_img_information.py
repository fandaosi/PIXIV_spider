"""
以下为通过作者ID下载该作者所有图片的一个demo，仅作参考
"""
from fuction import get_author_img_dic,get_author_illusts,\
                    get_img_dic,get_img_imformation,download
import os
if __name__ == '__main__':
    #打开作者ID的txt文件，一个ID为一行
    file = open('作者ID的txt文件',encoding='utf-8')
    while True:
        #去除换行符
        author_id = file.readline().replace('\n','')
        #根据作者ID得到插画ID
        author_img_dic = get_author_img_dic(author_id,'用户名','密码')
        illusts_list = get_author_illusts(author_img_dic)
        #根据作者ID得到下载信息
        for img_id in illusts_list:
            img_dic = get_img_dic(img_id,'用户名','密码')
            address = '保存地址' + img_dic['authorName']
            #创建以画师为名的文件夹作为图片存放路径
            #try语句是为了去除重复创建文件夹带来的异常
            try:
                os.mkdir(address)
            except:
                img_imformation = get_img_imformation(img_dic)
                # 根据下载信息下载
                download(img_imformation, address)
            else:
                img_imformation = get_img_imformation(img_dic)
                #根据下载信息下载
                download(img_imformation, address)
        if author_id == '':
            break
    file.close()