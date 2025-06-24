# Bookwalkerライトノベルランキング自動クローラー

## 機能概要
- Bookwalkerのライトノベルランキングを毎月1日・16日午前2時に自動で取得し、MySQLデータベースに保存します。
- 各書籍のカバー画像（表紙）も自動でダウンロードし、ローカルフォルダに保存します。
- FastAPIによるランキングデータのAPI提供。

## 使い方
### 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### MySQLの準備
- データベース名: `bookwalker`
- テーブル名: `light_novel_rank`
- テーブルは自動作成されます。
- 必要に応じて`bookwalker_crawler_selenium.py`内のMySQL接続情報を修正してください。

### クローラーの起動
```bash
python3 bookwalker_crawler_selenium.py
```
- スケジューラーが起動し、毎月1日・16日午前2時に自動でランキングを取得します。
- 取得したデータは`bookwalker_light_novel_YYYY-MM-1.xlsx`や`bookwalker_light_novel_YYYY-MM-2.xlsx`としてエクスポートされます。
- カバー画像は`YYYY-MM-1`や`YYYY-MM-2`フォルダ内にランキング番号（1.jpg, 2.jpg, ...）で保存されます。

## APIエンドポイント
FastAPIでランキングデータを取得できます。

- 例: `http://127.0.0.1:8000/rank/?period_tag=2024-06-1`
- `period_tag`は`YYYY-MM-1`または`YYYY-MM-2`形式です。

## MySQLテーブル構造
```sql
CREATE TABLE IF NOT EXISTS light_novel_rank (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `rank` INT,
    title VARCHAR(255),
    author VARCHAR(255),
    price VARCHAR(64),
    rating VARCHAR(16),
    url VARCHAR(512),
    period_tag VARCHAR(16),
    cover_path VARCHAR(512)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 注意事項
- ChromeDriverが必要です。バージョンに注意してください。
- 画像保存先やDB設定は必要に応じて変更してください。
- 本ツールは学術・個人利用を想定しています。

---

### English Summary

This repository provides a Python crawler for the BOOK☆WALKER monthly light novel ranking.  
It automatically fetches the full ranking (with Selenium), saves the data to both Excel and MySQL, and supports scheduled crawling (1st and 16th of each month) with Japanese comments and output.

---

ご質問・ご要望はIssueまたはPRでどうぞ！
