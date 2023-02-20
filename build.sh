docker build --platform linux/amd64 -t registry.cn-hangzhou.aliyuncs.com/space_smu/mis-test .
docker login --username=yxxxxie registry.cn-hangzhou.aliyuncs.com
docker push registry.cn-hangzhou.aliyuncs.com/space_smu/mis-test