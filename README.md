# discord-py-cord-template

Python Discord Bot(py-cord版) 基礎骨架

## 食用方法

食用要求:

1. python 版本 >= 3.8
2. ~~空腹 ( 怕你吃到吐 ) 😑~~

### pipenv

使用外部函數庫 [pipenv](https://pypi.org/project/pipenv/)

```sh
pip install pipenv # 安裝 pipenv
pipenv install
```

### venv

使用 python 內建函數庫 [venv](https://docs.python.org/zh-tw/3/tutorial/venv.html)

- 生產中使用

```sh
pip install -r requirements/prod.txt
```

- 開發中使用

```sh
pip install -r requirements/dev.txt
```

### python

將函數庫直接下載到全域

- 生產中使用

```sh
pip install -r requirements/prod.txt
```

- 開發中使用

```sh
pip install -r requirements/dev.txt
```

## 檔案結構

```python
├─.vscode # 編輯器設定
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
└─logs # 日誌存放
   └ [filename].log # 日誌
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

#### message command

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
