# 公式イメージをベースに使用
FROM python:3.9-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 現在のディレクトリの内容をコンテナ内の/appにコピー
COPY . /app

# requirements.txtに指定されているパッケージをインストール
RUN pip install --no-cache-dir -r requirements.txt

# 外部に5000番ポートを公開
EXPOSE 5000

# 環境変数を定義
ENV FLASK_APP wsgi.py

# コンテナが起動した時にapp.pyを実行
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
