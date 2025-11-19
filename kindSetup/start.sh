#!/usr/bin/bash
kubectl apply -f app_k8s/NameSpace/
kubectl apply -f app_k8s/Api/
kubectl apply -f app_k8s/Monitor/
kubectl apply -f app_k8s/Client/
kubectl apply -f app_k8s/Nginx/

