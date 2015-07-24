```shell
$ kubectl create -f ./tornado-service-rc.yaml

$ kubectl get pods -l app=tornado-service -o wide
NAME                    READY     STATUS    RESTARTS   AGE       NODE
tornado-service-5337a   1/1       Running   0          16m       ip-172-20-0-102.ec2.internal
tornado-service-na8o8   1/1       Running   0          16m       ip-172-20-0-103.ec2.internal

$ kubectl create -f ./tornado-service-svc.yaml

$ kubectl get svc
NAME         LABELS                                    SELECTOR              IP(S)         PORT(S)
kubernetes   component=apiserver,provider=kubernetes   <none>                10.0.0.1      443/TCP
tornadosvc   app=tornado-service                       app=tornado-service   10.0.102.32   10001/TCP

$ kubectl scale rc tornado-service --replicas=0; kubectl scale rc tornado-service --replicas=2;
(Distribute pods into different nodes)

$ kubectl create -f ./curlpod.yaml

$ kubectl get pods
NAME                    READY     STATUS    RESTARTS   AGE
curlpod                 1/1       Running   0          7m
tornado-service-5337a   1/1       Running   0          18m
tornado-service-na8o8   1/1       Running   0          18m

$ kubectl get services kube-dns --namespace=kube-system
NAME       LABELS                                                                           SELECTOR           IP(S)       PORT(S)
kube-dns   k8s-app=kube-dns,kubernetes.io/cluster-service=true,kubernetes.io/name=KubeDNS   k8s-app=kube-dns   10.0.0.10   53/UDP
                                                                                                                           53/TCP
$ kubectl exec curlpod -- nslookup tornadosvc
Server:    10.0.0.10
Address 1: 10.0.0.10 ip-10-0-0-10.ec2.internal

Name:      tornadosvc
Address 1: 10.0.102.32 ip-10-0-102-32.ec2.internal
`````
