FROM python:3

WORKDIR /usr/src/XTax

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./*.py ./

COPY ./*.yaml ./

ENTRYPOINT ["tail", "-f", "/dev/null"]
#ENTRYPOINT [ "python", "./CalcMyTax.py" ]