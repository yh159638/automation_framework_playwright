# 測試框架使用手冊

這份文件依照目前專案的實際程式碼整理，重點是描述目前已存在的設計與執行方式，而不是未來理想架構。若要維護或擴充這個框架，先理解目前的資料流與分層方式是最重要的。

## 1. 專案現況概述

目前專案使用的是：
- Python
- Pytest
- Playwright
- YAML 環境設定

它的整體思路是以最簡單的 Page Object Model 方式來組織測試：
- `testCase/`：測試案例
- `page/`：頁面定位與元素定義
- `scripts/`：業務流程
- `env/`：執行環境設定

## 2. 目前程式碼實際如何運作

### 2.1 根目錄 `conftest.py`
根目錄的 `conftest.py` 會先讀取 pytest 參數 `--env`。

```python
parser.addoption(
    "--env",
    action="store",
    default="local",
    choices=["local", "ut", "sit", "uat"],
    help="透過'--env'決定執行環境"
)
```

接著：

```python
env = request.config.getoption("--env")
env_config_file = root_dir / 'env' / 'env_config' / f'{env}_config.yaml'
env_config = read_yaml(env_config_file)
SessionConfig.BASE_DIR = root_dir
SessionConfig.ENV_CONFIG = env_config
```

這代表：
- pytest 啟動時會先決定執行環境
- 讀取相對應 YAML 設定檔
- 將設定寫入 `SessionConfig`，供後續 fixture 使用

### 2.2 環境設定檔
`env/env_config/` 下的檔案範例如下：

```yaml
test_url: "https://www.momoshop.com.tw/main/Main.jsp"
```

這是目前測試真正進入的網站 URL。若要切換環境，只要啟動 pytest 時帶不同 `--env` 值即可。

### 2.3 `SessionConfig`
`env/session_config.py` 定義：

```python
@dataclass
class SessionConfig:
    BASE_DIR: Path
    ENV_CONFIG: dict
```

目前只是簡單的資料容器，資料內容由 root `conftest.py` 讀取後注入。

## 3. Browser fixture 與測試啟動流程

`testCase/conftest.py` 中定義 `browser_driver` fixture：

```python
@pytest.fixture(scope="function")
def browser_driver():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"], ignore_default_args=["--enable-automation"])
        context = browser.new_context()
        page = context.new_page()
        page.goto(SessionConfig.ENV_CONFIG["test_url"])
        yield page
        context.close()
        browser.close()
```

這個 fixture 的作用是：
- 啟動 Playwright
- 建立 Chromium browser
- 建立新的 context 與 page
- 進入指定 URL
- 測試結束後關閉 browser

也就是說，每個測試都會獨立拿到一個 browser/page 實例，避免相互污染。

## 4. Test / Script / Page 的實際資料流

### 4.1 測試案例
`testCase/test_demo.py`：

```python
import pytest
from scripts.searchScript import search

@pytest.mark.demo
def test_google_search(browser_driver):
    search(browser_driver)
```

這個測試非常短，主要就是呼叫 `search()`。

### 4.2 頁面物件
`page/FrontPage.py`：

```python
class FrontPage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input: Locator = page.locator("//input[@name='search-input']")
        self.search_button: Locator = page.locator("//button[normalize-space()='搜尋']")
```

這裡將元素定位直接封裝在 page 類別內，方便 script 層重複使用。

### 4.3 業務流程
`scripts/searchScript.py`：

```python
def search(page):
    gp = FrontPage(page)

    gp.search_input.fill("3C")
    gp.search_button.click()
    gp.page.wait_for_timeout(2000)
```

這段程式碼是目前專案最重要的流程樣例：
1. 建立 `FrontPage`
2. 在搜尋框輸入 `3C`
3. 點擊搜尋按鈕
4. 等待 2 秒後結束

## 5. 目前的運行方式

### 5.1 安裝依賴

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install
```

### 5.2 執行單一測試

```bash
.\.venv\Scripts\python.exe -m pytest testCase\test_demo.py -q
```

### 5.3 指定環境

```bash
.\.venv\Scripts\python.exe -m pytest testCase\test_demo.py --env local -q
```

### 5.4 使用 `run.py`

根目錄的 `run.py` 目前僅簡單包裝 pytest：

```python
import pytest

pytest.main()
```

執行方式：

```bash
.\.venv\Scripts\python.exe run.py
```

## 6. 命名與維護建議

目前程式碼的命名已經相對固定，建議維持：

- `page/*.py`：頁面命名，例如 `FrontPage.py`
- `scripts/*.py`：業務流程命名，例如 `searchScript.py`
- `testCase/*.py`：測試案例命名，例如 `test_demo.py`

這樣做的好處是：
- 目錄橫向很清楚
- 新增案例時比較容易定位邏輯位置
- 其他工程師快速讀懂資料流

## 7. 目前專案的特點

這個專案目前最大的特點是：
- 架構簡單，容易學習
- Page Object 的分層邏輯清楚
- Playwright 的真實瀏覽器操作
- 可透過 `--env` 讀取不同環境設定

這使它很適合作為：
- 小型測試專案
- 內部專案原型
- 後續成長的基礎骨架

## 8. 目前還未完善的部分

從現在的程式碼看，仍有幾個值得補強的點：

1. `pytest.ini` 沒有註冊自訂 marker
   - 目前 `@pytest.mark.demo` 會存在，但沒有明確定義 marker。

2. `browser_driver` 直接使用固定網站 URL
   - 目前是從 YAML 讀取，但仍以單一網站為主。

3. `page` 層 selector 直接寫在類別中
   - 若網站變更，維護成本會上升。

4. 缺少報告與截圖機制
   - 目前沒有 Allure 或 HTML report 整合。

5. 缺少共用基底類別與 utility
   - 例如 `base_page.py`、`selectors.py`、`config.py` 等等。

## 9. 擴充方式建議

若要在現有架構上延伸，建議依序增加：

- `base_page.py`：封裝 `click`、`fill`、`wait` 等共用方法
- `selectors.py`：集中管理所有 selector
- `config.py`：管理 timeout、base url、browser 設定
- `report/`：輸出測試報告與失敗截圖
- `data/`：測試資料管理

這樣可以在不重構整個專案的情況下，逐步提升可維護性。

## 10. 結論

目前這個專案的實際狀態是「簡單但可擴充的 Playwright 測試骨架」。它已經具備：
- 測試案例入口
- 基本 POM 架構
- Environment 管理
- Playwright 瀏覽器起動
- 可重用的搜尋流程範例

未來若要成為真正可維護的自動化測試框架，重點在於補強環境抽象、selector 管理、報告整合與可重用的基礎元件，而不是重寫整套架構。
