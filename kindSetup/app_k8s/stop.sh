#!/bin/bash
kubectl delete -f DB/.
kubectl delete -f Monitor/.
kubectl delete -f Api/.
kubectl delete -f Client/.
kubectl delete -f Nginx/.
kubectl delete -f NameSpace/.
exit 0