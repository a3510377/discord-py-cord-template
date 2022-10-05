[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

# discord-py-cord-template

Python Discord Bot(py-cord版) 基礎骨架

## ⚡ Introduction 簡介

提供一個基本骨架，快速的開始一隻新的機器人開發

- Cog 架構
- For (初學者/開發者)
- Bot 指令/類別/功能 分離
- I18n 多語言支持
- Logging 日誌系統

## 食用方法

> 食用要求:
> python 版本 `>= 3.8`
> ~~空腹 ( 怕你吃到吐 ) 😑~~

### 📥 安裝

- **`pip`**: 將函數庫直接下載到全域

  - 生產中使用

  ```sh
  pip install -r requirements/prod.txt
  ```

  - 開發中使用

  ```sh
  pip install -r requirements/dev.txt
  ```

- **`venv`**: 使用 python 內建函數庫 [venv](https://docs.python.org/zh-tw/3/tutorial/venv.html)

  - 生產中使用

  ```sh
  pip install -r requirements/prod.txt
  ```

  - 開發中使用

  ```sh
  pip install -r requirements/dev.txt
  ```

- **`pipenv`**: 使用外部函數庫 [pipenv](https://pypi.org/project/pipenv/)

  ```sh
  pip install pipenv # 安裝 pipenv
  pipenv install
  ```

### 配置

將 `.env.example`  重新命名為 `.env` 並自行修改設定檔裡的資料。

### 執行

```sh
python -m bot
```

## 🔩 Folder structure 資料夾結構

```yml
/ # 根目錄
├─.vscode # 編輯器設定
│ ├ extensions.json # vscode 建議插劍
│ └ settings.json # vscode 插劍設定
├─bot # 原代碼資料夾
│ ├─cogs # cog 資料夾
│ │ ├─admin # 管理類 cog 存放
│ │ │ ├─i18n # 多語言資料
│ │ │ │ ├ clear.yaml # 給予上層 clear.py 的多語言檔案
│ │ │ │ └ # [上層 cog 存放處檔案名].{yaml,yml,json}
│ │ │ ├ clear.py # 清除訊息指令程式
│ │ │ └ # 您其它的 cog 檔案 ( 請模仿 ./clear.py 的檔案架構 ) 
│ │ └─ # 您其它的 cog 資料夾 ( 請模仿 ./admin 的資料夾結構 )
│ ├─core # 核心功能
│ │ ├ bot.py # 機器人核心程式
│ │ ├ events.py # 核心事件
│ │ ├ commands.py # 核心指令
│ │ ├ i18n.py # 多語言支持
│ │ ├ logging.py # 日誌支持
│ │ └ # 可依自己需求添加其他檔案
│ ├─utils # 小型函數庫
│ │ ├ __init__.py  # 程式導入點
│ │ ├ base.py # 自訂擴展
│ │ ├ util.py # 雜項函數
│ │ └ # 可依自己需求添加其他檔案
│ ├ __init__.py # 主程式導入點
│ └ __main__.py # 主程式進入點
├─env # 如果您使用 venv 將會生成該資料夾存放函數庫文件
├─logs # 日誌存放
│ └ [filename].log # 日誌
├─requirements # 日誌存放
│ ├ prod.txt # 生產用函數庫使用
│ └ dev.txt # 開發用函數庫使用
├ .dockerignore # docker 忽略設定檔
├ .editorconfig # editorconfig 設定檔
├ .env # 您的機密文件
├ .env.example # 範例機密文件
├ .flake8 # python-flask
├ .gitattributes # git 屬性設定
├ .gitignore # git 文件規則設定
├ .prettierrc.yaml # prettier 設定檔
├ Dockerfile # Docker 編譯設定
├ LICENSE # MIT License 希望您可以保留該文件讓大家可以更了解這個模板
├ Pipfile # Pipenv 設定檔
├ Pipfile.lock # Pipenv 緩存檔
└ README.md # 本文件
```

## 使用函數庫

|   函數庫名    | 描述                 |
| :-----------: | -------------------- |
|    py-cord    | discord api 支援     |
| python-dotenv | 讀取 `.env` 檔案     |
|     rich      | 日誌寫入/顯示        |
|    pyyaml     | 讀取 `yaml` 格式文件 |

### 開發中使用

| 函數庫名 | 描述            |
| :------: | --------------- |
|  black   | python 格式化器 |
|  flake8  | python 程式統一 |

## 內建功能

### 事件

1. `on_ready`
  打印出開機訊息
2. `on_application_command`
  slash_command 日誌
3. `on_application_command_error`
  slash_command 錯誤日誌
4. `on_command`
  message command 日誌
5. `on_command_error`
  message command 錯誤日誌

### 指令

#### slash_command

1. `delete`
  清除特定訊息。( 從訊息 ID )
  用戶執行權限需求 -> `manage_messages`
2. `purge`
  清除多個訊息。
  用戶執行權限需求 -> `manage_messages`
3. `uptime`
  獲取機器人上線時長
  用戶執行權限需求 -> `無`

#### message_command

1. `reload`
  重加載所有 `cog`
  用戶執行權限需求 -> `bot owner`

#### context_menus

無

#### user_commands

無

## 開發人員

<a href="https://github.com/a3510377" style="border-radius:50%">
    <img width="100px" src="https://cdn.discordapp.com/avatars/688181698822799414/f6534feffc3f15cf439cb2fdd579aab5.webp?size=128">
</a>
