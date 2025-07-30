FROM public.ecr.aws/lambda/python:3.11

RUN yum -y install poppler-utils

COPY app/requirements.txt ./
RUN pip3 install -r requirements.txt

COPY app/* ./

CMD ["lambda_function.lambda_handler"]
