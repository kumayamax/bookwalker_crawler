# BOOK☆WALKER ライトノベル月間ランキング自動クローラー

このリポジトリは、BOOK☆WALKER https://bookwalker.jp/rank/ct3/
のライトノベル月間ランキングを自動で取得し、ExcelファイルおよびMySQLデータベースに保存するPythonスクリプトを提供します。

- Seleniumによる自動スクロール＆全件取得
- APSchedulerによる毎月1日・16日の定時実行
- 取得データは期別（YYYY-MM-1/2）で管理
- 日本語コメント＆出力対応
- MySQL自動テーブル作成・保存
- Excelファイルも自動エクスポート

## 使い方

1. 必要なPythonパッケージをインストール
2. MySQLの設定を自分の環境に合わせて修正
3. `python3 bookwalker_crawler_selenium.py` で手動実行、またはスケジューラーで自動実行

---

### English Summary

This repository provides a Python crawler for the BOOK☆WALKER monthly light novel ranking.  
It automatically fetches the full ranking (with Selenium), saves the data to both Excel and MySQL, and supports scheduled crawling (1st and 16th of each month) with Japanese comments and output.

---

ご質問・ご要望はIssueまたはPRでどうぞ！
