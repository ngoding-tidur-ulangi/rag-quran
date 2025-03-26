FROM python:3.10

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

COPY --chown=user requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/cache/torch/sentence_transformers && \
    chmod -R 777 /app/cache

ENV TORCH_HOME=/app/cache

COPY --chown=user . .

RUN python prepare.py

EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
