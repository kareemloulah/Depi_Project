#!/bin/bash
kubectl apply -f NameSpace/.
kubectl apply -f DB/.
kubectl apply -f Monitor/.
kubectl apply -f Api/.
kubectl apply -f Client/.
kubectl apply -f Nginx/.
exit 0