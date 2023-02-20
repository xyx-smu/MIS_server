FROM python:3.9
COPY ./requirements.txt /
RUN python -m pip install --upgrade pip -i https://pypi.douban.com/simple
#RUN  pip3 install --user --upgrade pip
RUN  pip3 install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt
COPY ./ /mis-server
WORKDIR /mis-server
EXPOSE 8012
CMD ["python", "manage.py", "runserver", "0.0.0.0:8012"]