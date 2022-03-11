FROM python:3.9
COPY ./requirements.txt /
RUN  pip3 install --user --upgrade pip
RUN  pip3 install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
COPY ./ /tj_fund_server
WORKDIR /tj_fund_server
EXPOSE 8002
CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]

