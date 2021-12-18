import socket
import requests
import json

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('0.0.0.0', 5701))
server.listen(3)


def group_msg(group_id, msg):
    requests.get(f'http://127.0.0.1:5700/send_group_msg?group_id={group_id}&message={msg}')


def private_msg(user_id, p_msg):
    requests.get(f'http://127.0.0.1:5700/send_private_msg?user_id={user_id}&message={p_msg}')


if __name__ == '__main__':
    req = requests.Session()
    req.trust_env = False
    keyword = ['/wh|', '/rs', '/rp18', '/ls', '/rp']
    while True:
        conn, address = server.accept()

        data = str(conn.recv(1024).decode('utf-8').split('\r\n\r\n')).split(',')
        if 'interval' not in data[1]:
            if 'group' in data[7]:
                rec_msg_g = data[4].split(':')[1].split('"')[1]
                group_id = data[3].split(':')[1]
                nickname = data[15].split(':')[1].split('"')[1]
                user_id = data[19].split(':')[1][:-1]

                if rec_msg_g == '/ls':
                    menu = '/ls -> 显示此页\n' \
                           '/wh|地区 -> 天气\n' \
                           '/rs -> 获取随机一句话\n' \
                           '/rp18 -> 获取随机色图\n'
                    group_msg(group_id, menu)
                elif '/wh' in rec_msg_g and '|' in rec_msg_g:
                    city = rec_msg_g.split('|')[1].strip()
                    r = req.post(f'https://api.moonwl.cn/api/wea/wea.php?city={city}')
                    try:
                        data = json.loads(r.text)['data']
                        text = f"""
  地区: {city}
  天气:{data["forecast"][0]['type']}
  最{data["forecast"][0]['high']}
  最{data["forecast"][0]['low']}
  风向: {data["forecast"][0]['fengxiang']}"""
                        group_msg(group_id, text)
                    except KeyError:
                        group_msg(group_id, f'[CQ:at,qq={user_id}]\n城市信息错误')

                elif rec_msg_g == '/rs':
                    sentence = requests.get(
                        'https://api.imjad.cn/hitokoto/?cat=e&charset=utf-8&length=50&encode=&fun=sync&source=').text
                    text = f'[CQ:at,qq={user_id}]\n{sentence}'
                    group_msg(group_id, text)

                elif rec_msg_g == '/rp18':
                    text = f'  [CQ:at,qq={user_id}] \n  你在想屁吃 '
                    group_msg(group_id, text)
                elif rec_msg_g == '/rp':
                    r = req.get('https://www.loliapi.com/acg/?return=json')
                    url = json.loads(r.text)['imgurl']
                    text = f'[CQ:at,qq={user_id}]\n[CQ:image,file={url}]'
                    group_msg(group_id, text)

                elif '/' in rec_msg_g and rec_msg_g not in keyword:
                    group_msg(group_id, f'未定义的函数{rec_msg_g}')
