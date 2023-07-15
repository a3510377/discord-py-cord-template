FROM python:3.11.4-alpine as base
FROM base as builder

COPY requirements/prod.txt /requirements.txt
RUN pip install --user -r /requirements.txt

FROM base
WORKDIR /base

COPY --from=builder /root/.local /root/.local
COPY ./bot ./bot

ENV PATH=/root/.local:$PATH

CMD ["python", "-m", "bot"]
