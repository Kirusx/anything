# _*_ coding:utf-8 _*_
import docker
from harborclient import harborclient


def docker_client():
    host = "172.16.10.10"
    user = "admin"
    password = "Harbor12345"
    client = harborclient.HarborClient(host, user, password, protocol='https')
    return client

