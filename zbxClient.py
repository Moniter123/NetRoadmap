#!/usr/bin/python
# -*- coding:utf-8 -*-

'''
Func: get the core API of app server, then sync to zabbix web scenario
Created on 2017/06/10
@author: lowry
'''

import json
import os, sys
import re
import requests

# influxdb
i_username = 'xxx'
i_password = 'yyy'
i_database = 'db_name'


class ZbxClient(object):
    def __init__(self):
        self.url = "http://{zabbix-host}/zabbix/api_jsonrpc.php"
        self.user = "xxx"
        self.password = "yyy"
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

        # include hosts list --- for example
        host_lists = {"app1_name":"127.0.0.1","app2_name":"127.0.0.1","app3_name":"127.0.0.1",}

        #struct data --- for example
        struct_datas = [{"elementType": "node", "host": "app1_name", "ip": "127.0.0.1", "x": 255, "y": 25, "id": 6375,"img": "cloud.jpg", "text": "internet (1M)", "value": "0", "limit": "1 M", "level": 0}]

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