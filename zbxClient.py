#!/usr/bin/python
# -*- coding:utf-8 -*-

'''
Func: get the core API of app server, then sync to zabbix web scenario
Created on 2017/06/10
@author: youjiaLee
'''

import json
import os, sys
import re
import requests

# influxdb
i_username = 'admin'
i_password = 'Dianrong.com.cn'
i_database = 'dr_container_running_status'


class ZbxClient(object):
    def __init__(self):
        self.url = "http://zabbix.sl.com/zabbix/api_jsonrpc.php"
        self.user = "devops"
        self.password = "Dianrong123$"
        self.headers = {"Content-Type": "application/json"}
        self.setup_host_name = "http_checker"
        self.authID = self.user_login()

    def get_data(self, post_data):
        try:
            response_json = requests.post(self.url, data=post_data, headers=self.headers).json()
            if response_json.get("error"):
                raise RuntimeError("error:{0}".format(str(response_json.get("error"))))
            return response_json
        except Exception, e:
            print e


    def user_login(self):
        """
            用户登录，获取authid
            params: user/password
            return: authid
        """
        post_data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "user.login",
                "params": {
                    "user": self.user,
                    "password": self.password
                },
                "id": 0
            })
        result = self.get_data(post_data)["result"]
        return result


    def hostids_get(self):
        """
            retrieve all data about web scenario
            return: 初始化hostid和applicationid, 返回所有httptest的httptestid
        """
        try:
            host_list = []
            host_data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "host.get",
                    "params": {
                        "output": ["hostid", "host"],
                    },
                    "auth": self.authID,
                    "id": 1
                })
            res = self.get_data(host_data)
            return res['result']
        except Exception, e:
            print e

    def hostinterface_get(self, hostid):
        """
            retrieve all data about web scenario
            return: 初始化hostid和applicationid, 返回所有httptest的httptestid
        """
        try:
            host_list = []
            host_data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "hostinterface.get",
                    "params": {
                        "output": "extend",
                        "hostids": hostid
                    },
                    "auth": self.authID,
                    "id": 1
                })
            res = self.get_data(host_data)
            return res
        except Exception, e:
            print e

    def itemid_get(self, key_name, hostid):

        try:
            item_data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "item.get",
                    "params": {
                        "output": "extend",
                        # "output": "itemids",
                        "hostids": hostid,
                        "search": {
                            "key_": key_name  # 提供具体item
                        }
                    },
                    "auth": self.authID,
                    "id": 1
                })
            res = self.get_data(item_data)
            return res
        except Exception, e:
            print e

    def history_get(self, itemid):
        try:
            item_list = []
            history_data = json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "history.get",
                    "params": {
                        "output": "extend",
                        "history": 0,
                        "itemids": "40281",
                        "sortfield": "clock",
                        "sortorder": "DESC",
                        "limit": 10
                    },
                    "auth": self.authID,
                    "id": 1
                })
            res = self.get_data(history_data)
            print res
        except Exception, e:
            print e


    def getStructDatas(self):
        # init the object of zabbix API
        zbx_client = ZbxClient()  # prod

        # hostid_list = zbx_client.hostids_get()
        # for dic in hostid_list:
        #     try:
        #         host = dic['host']
        #         hostid = dic['hostid']
        #     except:
        #         pass

        # include hosts list
        host_lists = {"stnc-extranet":"211.148.20.97","fw201":"10.16.132.101","sw2-core1":"10.16.147.2","stnc-zabserver":"10.16.142.23","stnc_app_gateway":"10.16.142.1","main_dns_server":"10.16.78.202","spare_dns_server":"10.16.78.201","app204":"10.16.142.23","app205":"10.16.142.23","app206":"10.16.142.23","ucloud_proxy":"10.15.101.173","gds-extranet":"103.251.84.217","fw101":"10.16.68.101","sw1-core1":"10.16.64.17","gds_app_gateway":"10.16.78.1","sw_101":"10.16.76.43","nginx_vip":"10.16.74.240","lb101":"10.16.74.241","lb102":"10.16.74.242","applb-vip":"10.16.78.230","app120":"10.16.78.40","zabserver":"10.16.78.32","db101":"10.16.74.41","ora101":"10.16.76.11","db114":"10.16.76.43","zabbix_db":"10.16.76.43","nginx-vip":"10.16.74.240"}

        #struct data
        struct_datas = [{"elementType": "node", "host": "stnc-extranet", "ip": "211.148.20.97", "x": 255, "y": 25, "id": 6375,"img": "cloud.jpg", "text": "internet (100M)", "value": "0", "limit": "100 M", "level": 0},{"elementType": "node", "host": "fw201", "ip": "10.16.132.101", "x": 255, "y": 145, "id": 36975, "img": "ER16.jpg","text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "sw2-core1", "ip": "10.16.147.2", "x": 255, "y": 295, "id": 75225,"img": "5200.jpg", "text": "sw_core2", "value": "0", "limit": "100 M", "level": 0},{"elementType": "node", "host": "stnc-zabserver", "ip": "10.16.142.23", "x": 465, "y": 465, "id": 216225,"img": "server.jpg", "text": "", "value": "0", "limit": "100 M", "level": 0},{"elementType": "node", "host": "stnc_app_gateway", "ip": "10.16.142.1", "x": 255, "y": 465, "id": 118575,"img": "middle.jpg", "text": "sw_200", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "main_dns_server", "ip": "10.16.78.202", "x": 25, "y": 600, "id": 15000,"img": "server.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "spare_dns_server", "ip": "10.16.78.201", "x": 135, "y": 650, "id": 87750,"img": "server.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "app204", "ip": "10.16.142.23", "x": 255, "y": 600, "id": 153000,"img": "server.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "app205", "ip": "10.16.142.23", "x": 375, "y": 650, "id": 243750,"img": "server.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "app206", "ip": "10.16.142.23", "x": 495, "y": 600, "id": 297000,"img": "server.jpg", "text": "db206", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "ucloud_proxy", "ip": "10.15.101.173", "x": 1005, "y": 25, "id": 25125,"img": "cloud.jpg", "text": "ucloud (100M)", "value": "0", "limit": "100M", "level": 0},{"elementType": "node", "host": "gds-extranet", "ip": "103.251.84.217", "x": 1200, "y": 25, "id": 30000,"img": "cloud.jpg", "text": "internet (75M)", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "fw101", "ip": "10.16.68.101", "x": 1075, "y": 145, "id": 155875,"img": "ER16.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "sw1-core1", "ip": "10.16.64.17", "x": 1000, "y": 295, "id": 295000,"img": "5200.jpg", "text": "sw_core1", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "gds_app_gateway", "ip": "10.16.78.1", "x": 915, "y": 465, "id": 425475,"img": "2948.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "sw_101", "ip": "10.16.76.43", "x": 1215, "y": 465, "id": 564975,"img": "2948.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "nginx_vip", "ip": "10.16.74.240", "x": 1215, "y": 295, "id": 358425,"img": "2948.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "lb101", "ip": "10.16.74.241", "x": 1405, "y": 295, "id": 414475,"img": "server.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "lb102", "ip": "10.16.74.242", "x": 1405, "y": 395, "id": 554975,"img": "server.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "applb-vip", "ip": "10.16.78.230", "x": 750, "y": 600, "id": 450000,"img": "serve.jpg", "text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "app120", "ip": "10.16.78.40", "x": 879, "y": 650, "id": 571350,"img": "serve.jpg", "text": "app120", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "zabserver", "ip": "10.16.78.32", "x": 995, "y": 600, "id": 597000,"img": "serve.jpg", "text": "zabserver", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "db101", "ip": "10.16.74.41", "x": 1105, "y": 600, "id": 663000, "img": "8260.jpg","text": "", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "ora101", "ip": "10.16.76.11", "x": 1225, "y": 600, "id": 735000,"img": "8260.jpg", "text": "ora101", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "db114", "ip": "10.16.76.43", "x": 1355, "y": 570, "id": 772350,"img": "2948.jpg", "text": "db114", "value": "0", "limit": "0", "level": 0},{"elementType": "node", "host": "zabbix_db", "ip": "10.16.76.43", "x": 1485, "y": 673, "id": 999405,"img": "serve.jpg", "text": "10.16.76.43", "value": "0", "limit": "0", "level": 0},{"elementType": "linkNode", "host": "stnc-extranet", "nodeAid": 6375, "nodeZid": 36975, "text": "0", "level": 0},{"elementType": "linkNode", "host": "fw201", "nodeAid": 36975, "nodeZid": 75225, "text": "0", "level": 0},{"elementType": "linkNode", "host": "stnc-zabserver", "nodeAid": 118575, "nodeZid": 216225, "text": "0","level": 0},{"elementType": "linkNode", "host": "stnc_app_gateway", "nodeAid": 75225, "nodeZid": 118575, "text": "0","level": 0},{"elementType": "hostLink", "host": "main_dns_server", "nodeAid": 118575, "nodeZid": 15000, "text": "0","level": 0},{"elementType": "hostLink", "host": "spare_dns_server", "nodeAid": 118575, "nodeZid": 87750, "text": "0","level": 0},{"elementType": "hostLink", "host": "app204", "nodeAid": 118575, "nodeZid": 153000, "text": "0", "level": 0},{"elementType": "hostLink", "host": "app205", "nodeAid": 118575, "nodeZid": 243750, "text": "0", "level": 0},{"elementType": "hostLink", "host": "app206", "nodeAid": 118575, "nodeZid": 297000, "text": "0", "level": 0},{"elementType": "linkNode", "host": "ucloud_proxy", "nodeAid": 25125, "nodeZid": 155875, "text": "0", "level": 0},{"elementType": "linkNode", "host": "gds-extranet", "nodeAid": 30000, "nodeZid": 155875, "text": "0", "level": 0},{"elementType": "linkNode", "host": "fw101", "nodeAid": 155875, "nodeZid": 295000, "text": "0", "level": 0},{"elementType": "linkNode", "host": "sw1-core1", "nodeAid": 295000, "nodeZid": 425475, "text": "0", "level": 0},{"elementType": "linkNode", "host": "sw_101", "nodeAid": 295000, "nodeZid": 564975, "text": "0", "level": 0},{"elementType": "linkNode", "host": "nginx_vip", "nodeAid": 295000, "nodeZid": 358425, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "lb101", "nodeAid": 358425, "nodeZid": 414475, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "lb102", "nodeAid": 358425, "nodeZid": 554975, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "applb-vip", "nodeAid": 425475, "nodeZid": 450000, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "app120", "nodeAid": 425475, "nodeZid": 571350, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "gds_app_gateway", "nodeAid": 425475, "nodeZid": 597000, "text": "0","level": 0},{"elementType": "newHostLink", "host": "db101", "nodeAid": 564975, "nodeZid": 663000, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "ora101", "nodeAid": 564975, "nodeZid": 735000, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "db114", "nodeAid": 564975, "nodeZid": 772350, "text": "0", "level": 0},{"elementType": "newHostLink", "host": "zabbix_db", "nodeAid": 772350, "nodeZid": 999405, "text": "0","level": 0},{"elementType": "dedicatedLink", "host": "sw2-core1", "nodeAid": 75225, "nodeZid": 295000, "text": "0","level": 0}]

        new_struct_datas = []
        for hostname,ip in host_lists.items():
            try:
                icmppingloss = int(float(zbx_client.itemid_get("icmppingloss[" + ip + ",4]", str('10119'))['result'][0]['lastvalue']))    #zbx server112 hostids--》 10119

                icmpping = int(zbx_client.itemid_get("icmpping[" + ip + ",4]", str('10119'))['result'][0]['lastvalue'])

                icmppingsec = float(zbx_client.itemid_get("icmppingsec[" + ip + ",4]", str('10119'))['result'][0]['lastvalue']) * 1000      #s -> ms
                # setup value for level
                level = 0
                if icmppingloss > 30 or icmpping == 0 or icmppingsec > 400:
                    print "Alert hostname:",hostname
                    level = 1

                for struct_data in struct_datas:
                    """
                        1.node: level设定：判断是否触发告警
                        2.link: text 与 level设定：填充实时数据值；判断是否触发告警
                    """
                    if struct_data['host'] == hostname:
                        struct_data['level'] = level
                        struct_data['text'] = str(icmppingloss) + "%/" + str(icmpping) + "/" + str(icmppingsec) + "ms"
                        new_struct_datas.append(struct_data)
            except Exception,e:
                print "Alert hostname:", hostname
                for struct_data in struct_datas:
                    if struct_data['host'] == hostname:
                        struct_data['level'] = 1
                        struct_data['text'] = "null"
                        new_struct_datas.append(struct_data)
        return json.dumps(new_struct_datas)


if __name__ == '__main__':
    client = ZbxClient()
    struct_data_list = client.getStructDatas()
    print struct_data_list