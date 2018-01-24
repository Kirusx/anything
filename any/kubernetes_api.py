# _*_ coding:utf-8 _*_
import kubernetes.client


def kubecluster():
    cluster_instance = kubernetes.client.CoreV1Api()
    return cluster_instance


def getdeployment():
    deployment = kubernetes.client.AppsV1beta1Api()
    return deployment
