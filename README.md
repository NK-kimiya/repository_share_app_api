# 制作物：CodeBridge（コードブリッジ)　

デモの紹介サイト　

https://kimikou-blog.jp/portfolio/

## 🎯 目的・背景

ハッカソンに出場した際、私は「チームメンバーのスキルを把握するまでに時間がかかる」という課題を感じました。  
また、ChatGPTなど生成AIの進化により、GitHubのリポジトリを読み解きながら実装や学習を行うスタイルが、以前よりも取りやすくなってきたとも実感しました。

そこで私は、「リポジトリを共有し、質問や議論ができるWebアプリ」を開発しました。  
このアプリでは、チーム開発におけるスキル共有の円滑化と、学習者同士が技術知識を共有し合える環境の実現を目指して制作しました。

アプリの名前は **「CodeBridge（コードブリッジ）」** です。  
その由来は、“プログラミング（コード）を通じて、人と人とをつなぐ架け橋になりたい” という想いから名付けました。

---

## 🛠 使用した技術スタック

- **フロントエンド**：React  
- **バックエンド**：Django REST Framework、Express.js  
- **データベース**：SQLite（Django側）、MongoDB（Express/Socket側）  
- **リアルタイム通信**：Socket.io（Express）  
- **認証方式**：JWT（JSON Web Token）  
- **AIモデル**：PyTorch（BERTによる文章分類）  

---

## 📦 このリポジトリ（Django側）で実装されている主な機能

- **ユーザー管理**
  - カスタムユーザーモデル（メールログイン対応）
  - 認証・認可機能（JWT）

- **ルーム機能**
  - リポジトリ共有やチャット的なスペースの作成・参加

- **GitHubリポジトリ管理**
  - タイトル・説明・カテゴリ付きで登録・閲覧・検索

- **メッセージ機能**
  - 各リポジトリに紐づいたリアルタイム掲示板

- **お気に入り管理**
  - 気に入ったリポジトリのブックマーク保存

- **自然言語処理（BERT分類）**
  - 入力文を以下の5カテゴリに分類するAPIを提供：
    - `API`
    - `ECサイト`
    - `動画投稿アプリ`
    - `snsアプリ`
    - `WebRTC`

---

## 📚 使用されている主なライブラリ

- `transformers`（Hugging Face）：BERTモデルの活用  
- `torch`（PyTorch）：深層学習モデルの推論  
- `BertJapaneseTokenizer`：日本語テキストのトークン化  
- `uuid`：識別子生成  
- `requests`：外部API通信用  


## ⚙️ セットアップ方法

このプロジェクトは Django で構成されたバックエンドアプリです。以下の手順でローカル環境で動作確認が可能です。

・動作を確認した環境　

Python → v3.11.3　

pip → v22.3.1　


---

### 1. プロジェクトをクローン

```bash
git clone https://github.com/NK-kimiya/repository_share_app_api.git
cd repository_share_app_api
```

### 2. 仮想環境を作成
```
python -m venv venv
```

### 3. 仮想環境を有効化

```
・Windows
venv\Scripts\activate　

・Mac / Linux
source venv/bin/activate
```

### 4.必要なパッケージをインストール
```
pip install -r requirements.txt
```

### 5.マイグレーションを実行
```
・manage.py があるディレクトリへ移動
cd Repository_Share_Api
```

・モデル定義のマイグレーションファイルを作成
```
python manage.py makemigrations api
```

・実際にデータベースに反映
```
python manage.py migrate
```

### 6.スーパーユーザーを作成（任意のメールアドレスとパスワードを入力）
```
python manage.py createsuperuser
```

### 7. モデルのパスを変更

`classifier.py` の以下のコードにある `'your_model_directory_path_here'` の部分を、  
**あなたのローカル環境で `Repository_Share_API` フォルダが存在するルートパス**に置き換えてください。

```python
model_dir = Path(
    r'your_model_directory_path_here\Repository_Share_API\Repository_Share_Api\api\model_transformers'
).as_posix()
```




### 8.サーバーを起動（ポート8000を使用）
```
python manage.py runserver
アクセスURL（デフォルト）:
👉 http://127.0.0.1:8000/admin
```

## 🔗 関連リポジトリ

このDjango（バックエンドAPI）とは別に、以下の関連リポジトリも公開しています：

- 🌐 フロントエンド（React）
  - [https://github.com/NK-kimiya/repository_share_app_front](https://github.com/NK-kimiya/repository_share_app_front.git)
- 🔌 リアルタイムサーバー（Express + Socket.io）
  - [https://github.com/NK-kimiya/repository_share_app_socket](https://github.com/NK-kimiya/repository_share_app_socket.git)






