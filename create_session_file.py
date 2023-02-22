with open('proxy_list.txt', 'r') as file:
    proxy_list = file.readlines()
index = 0
ip = proxy_list[index].split(';')[0]
port = proxy_list[index].split(';')[1].split('\n')[0]