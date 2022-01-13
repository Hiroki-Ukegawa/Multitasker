# Multitasker

マルチタスク管理アプリです。  
タスク毎に完了度を設定することで、タスクを切り替えながら少しずつ進められるようにしています。  
レスポンシブ対応しているのでスマホからもご確認いただけます。

https://multitasker-app.herokuapp.com/  
【ゲスト用アカウント】  
メールアドレス：guest@guest.guest／パスワード：12345678

![screenshot](https://user-images.githubusercontent.com/66906495/149077476-e2253f70-d5ad-48cb-bc26-afa8b63348ea.jpg)


# 使用技術
* Python 3.8.11
* Flask 1.1.1
* Heroku
* Heroku Postgres
* SendGrid API

# 機能一覧
* ユーザー登録、ログイン（Flask-Login）
* タスク登録
* タスク完了度登録(Ajax)
* お問い合わせ、メール送信（SendGrid）
* 管理者用ページ