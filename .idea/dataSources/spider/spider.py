import os.path
import time
from itertools import repeat

import requests
from DataRecorder import Recorder
from bs4 import BeautifulSoup
from lxml import etree
from retrying import retry
from concurrent.futures import ThreadPoolExecutor, as_completed


headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "http://csujwc.its.csu.edu.cn",
        "Pragma": "no-cache",
        "Referer": "http://csujwc.its.csu.edu.cn/jiaowu/tkgl/queryKbBySj.jsp",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "cookie": 'JSESSIONID=16C19D509012E179F7223F41398A8F3E; SF_cookie_350=kZhXC5nraIekxJBHmV92zSUiapt0ZS/iDw6KIWlxe2k='
    }


@retry(stop_max_attempt_number=5)
def get_response(url, params, data):
    # time.sleep(0.1)
    response = requests.post(url, headers=headers, params=params, data=data, verify=False)
    if response.status_code != 200:
        print(response.status_code)
        print(response.text)
        raise Exception('请求失败')
    return response


def get_classroom():
    # 解析 HTML
    with open('教室select.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    select = soup.find('select', {'id': 'classroomID'})

    # 提取所有选项
    options = []
    for option in select.find_all('option'):
        value = option.get('value')
        text = option.text.strip()
        if value:  # 过滤掉空值的选项
            options.append((value, text))

    yxbh_dict = {}
    # 输出结果
    for value, text in options:
        yxbh_dict[text] = value

    return yxbh_dict


def get_detail(classroom_id, classroom_name, zc):
    if not os.path.exists(f'data/{classroom_name}'):
        os.makedirs(f'data/{classroom_name}')

    r = Recorder(f'data/{classroom_name}/第{zc}周.csv')
    r.add_data(['', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日'])
    jc_list = ['第一节', '第二节', '第三节', '第四节', '第五节', '第六节', '第七节', '第八节', '第九节', '第十节', '第十一节', '第十二节']

    item = [list(repeat('', 7)) for _ in range(12)]
    for xq in range(1, 7+1):
        for jc in range(1, 12+1):
            jc_name = jc_list[jc - 1]
            item[jc - 1][0] = jc_name
            print(f'采集 {classroom_name}-教室 第{zc}周 星期{xq} 节次{jc}')
            url = "http://csujwc.its.csu.edu.cn/tkglAction.do"
            params = {
                "method": "tzkb",
                "type": "1",
                "first": "no",
                "querySjcx": "1",
                "nj": ""
            }
            data = {
                "sql": "init",
                "m": "",
                "xnxqh": "2024-2025-2",
                "zc": f"{zc}",
                "xq": f"{xq}",
                "jc": f'{"{:02d}".format(jc)}',
                "xqid": "",
                "gnqid": "",
                "jzwid": "",
                "classroomID": classroom_id,
                "rxnf": "",
                "skyx": "",
                "kkyx": "",
                "kcmc": "",
                "kcid": "",
                "findType": "cx",
                "type2": "2"
            }
            response = get_response(url, params, data)

            html = etree.HTML(response.text)

            tbody = html.xpath('//div[@id="tag_tshowView"]/table/tbody')[0]
            td_list = tbody.xpath('./tr/td')
            if td_list:
                # 课程
                kc = td_list[4].xpath('./text()')[0].strip()
                # 教师
                js_name = ', '.join(td_list[5].xpath('./a/text()'))
                # 班级
                bj = td_list[1].xpath('./text()')[0].strip()

                item[jc-1][xq-1] = '; '.join([kc, js_name, bj])

    for i in item:
        r.add_data(i)
    r.record()


def main():
    classroom_dict = get_classroom()
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(get_detail, classroom_id, classroom_name, zc)
                   for classroom_name, classroom_id in classroom_dict.items()
                   for zc in range(1, 22+1)]
        for future in as_completed(futures):
            future.result()


if __name__ == '__main__':
    main()