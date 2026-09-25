# Automation Framework Playwright

這個專案是一個以 Python + Playwright + Pytest 為核心的 Web 自動化測試範例框架。它目前是以最小可運行架構呈現，目標是把測試案例、頁面元素、流程腳本與環境設定拆開，方便維護與擴充。

## 1. 專案簡介

目前這個專案的實際功能很簡單：
- 啟動 Playwright Chromium
- 讀取環境設定檔
- 打開指定的網站
- 依照頁面元素定位進行搜尋操作

核心技術：
- Python
- Pytest
- Playwright
- YAML 環境設定

## 2. 目前實際專案結構

```text
automation_framework_playwright/
├─ .gitignore
├─ README.md
├─ run.py
├─ pytest.ini
├─ requirements.txt
├─ conftest.py
├─ docs/
│  └─ framework-guide.md
├─ env/
│  ├─ session_config.py
│  └─ env_config/
│     ├─ local_config.yaml
│     ├─ sit_config.yaml
│     ├─ uat_config.yaml
│     └─ ut_config.yaml
├─ page/
│  └─ FrontPage.py
├─ scripts/
│  └─ searchScript.py
├─ testCase/
│  ├─ conftest.py
│  └─ test_demo.py
├─ util/
│  └─ read_file_function.py
├─ report/            # 執行 run.py 後自動產生的 Allure HTML 報告，已在 .gitignore 中忽略
└─ .venv/
```

## 3. 各層職責

### 3.1 `testCase/`
這裡是測試案例入口，目前只有一個範例：
- `test_demo.py`

實際測試內容：

```python
import pytest
from scripts.searchScript import search

@pytest.mark.demo
def test_online_store_search(browser_driver):
    search(browser_driver)
```

這代表測試函式本身很簡短，真正的頁面互動邏輯則由下層處理。

### 3.2 `page/`
`FrontPage.py` 定義頁面物件：

```python
class FrontPage:
    def __init__(self, page: Page):
        self.page = page
        self.search_input: Locator = page.locator("//input[@name='search-input']")
        self.search_button: Locator = page.locator("//button[normalize-space()='搜尋']")
```

目前的頁面定位器包含：
- `search_input`：搜尋輸入框
- `search_button`：搜尋按鈕
- `page`：Playwright 頁面實例

### 3.3 `scripts/`
`searchScript.py` 是業務流程層：

```python
def search(page):
    gp = FrontPage(page)

    gp.search_input.fill("3C")
    gp.search_button.click()
    gp.page.wait_for_timeout(2000)
```

這個腳本會：
1. 建立 `FrontPage`
2. 在搜尋框填入 `3C`
3. 點擊搜尋按鈕
4. 等待 2 秒確認頁面反應

### 3.4 `env/`
專案使用 `env/` 目錄來存放環境設定，設定檔格式為 YAML。

例如：

```yaml
test_url: "https://www.momoshop.com.tw/main/Main.jsp"
```

目前支援的環境選項在根目錄的 `conftest.py` 中定義：

```python
parser.addoption(
    "--env",
    action="store",
    default="local",
    choices=["local", "ut", "sit", "uat"],
    help="透過'--env'決定執行環境"
)
```

這表示執行測試時可透過 `--env` 指定不同環境設定，例如：
- `--env local`
- `--env sit`
- `--env uat`

### 3.5 `util/`
`read_file_function.py` 會讀取 YAML 檔並回傳 `dict`，供環境設定注入到 `SessionConfig`。

## 4. 環境設定與執行流程

### 4.1 `SessionConfig`
`env/session_config.py` 定義了共享設定物件：

```python
@dataclass
class SessionConfig:
    BASE_DIR: Path
    ENV_CONFIG: dict
```

程式在 `conftest.py` 中會先讀取目前環境的 YAML，再把結果存入 `SessionConfig`。

### 4.2 全域 `conftest.py`
根目錄的 `conftest.py` 會在 pytest 啟動前執行，做的事情是：
- 解析 `--env` 參數
- 讀取 `env/env_config/{env}_config.yaml`
- 設定 `SessionConfig.BASE_DIR`
- 設定 `SessionConfig.ENV_CONFIG`

### 4.3 Browser fixture
`testCase/conftest.py` 定義 `browser_driver` fixture：

```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--start-maximized"], ignore_default_args=["--enable-automation"])
    context = browser.new_context()
    page = context.new_page()
    logging.info("Browser launched successfully.")
    logging.info("Goto test website.")
    page.goto(SessionConfig.ENV_CONFIG["test_url"])
```

這個 fixture 會為每個測試建立新的 page，過程中會透過 `logging` 輸出啟動狀態，並在測試結束後關閉 browser。

## 5. 安裝與執行

### 5.1 建立虛擬環境

#### 請把 env_example 的檔名改為 env

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install
```

#### （選用）安裝 Allure commandline

`run.py` 執行完測試後會嘗試呼叫 Allure commandline 把結果轉成 HTML 報告。這個 CLI 不是 pip 套件，需要另外安裝，並確保可執行檔在 `PATH` 中，同時需要 Java 8 以上的執行環境（JRE/JDK）。

Windows 上可透過 scoop 安裝：

```bash
scoop install allure
```

或透過 npm 安裝：

```bash
npm install -g allure-commandline
```

如果沒有安裝 Allure，`run.py` 仍會照常執行 pytest，只會在終端機印出警告並略過報告產生。

### 5.2 執行測試

```bash
.\.venv\Scripts\python.exe -m pytest testCase\test_demo.py -q
```

如果要指定環境：

```bash
.\.venv\Scripts\python.exe -m pytest testCase\test_demo.py --env local -q
```

### 5.3 使用專案入口

`run.py` 目前的邏輯是「執行 pytest 並自動產生 Allure HTML 報告」：

```python
def main() -> int:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    report_dir = ROOT_DIR / "report" / timestamp
    raw_results_dir = tempfile.mkdtemp(prefix="allure-results-")

    try:
        exit_code = pytest.main(sys.argv[1:] + ["--alluredir", raw_results_dir])
        generate_allure_report(raw_results_dir, report_dir)
    finally:
        shutil.rmtree(raw_results_dir, ignore_errors=True)

    return exit_code
```

執行流程：
1. 建立一個以時間戳記命名的輸出目錄 `report/<yyyyMMddHHmmss>/`
2. 用暫存資料夾接收 pytest 執行過程中產生的 allure raw results（`--alluredir`）
3. 呼叫 `allure generate` 把 raw results 轉成 HTML 報告，輸出到 `report/<timestamp>/`
4. 不論成功或失敗，都會清除暫存的 raw results 資料夾
5. 找不到 Allure commandline 時只會印出警告，不會讓測試失敗

可直接執行：

```bash
.\.venv\Scripts\python.exe run.py
```

執行完成後，開啟 `report/<timestamp>/index.html` 即可查看報告。

## 6. `pytest.ini` 設定

目前 `pytest.ini` 內容只有 logger 設定：

```ini
[pytest]

log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)s] %(message)s (%(filename)s:%(lineno)s)
log_cli_date_format = %Y-%m-%d %H:%M:%S
```

這代表專案現在沒有明確註冊自訂 mark，例如 `@pytest.mark.demo`。如果後續要統一管理 marker，建議補充：

```ini
[pytest]
markers =
    demo: demo test scenario
```

## 7. 使用方式與擴充建議

### 7.1 新增 Page Object
在 `page/` 新增頁面類別，例如：

```python
class LoginPage:
    def __init__(self, page):
        self.page = page
        self.username = page.locator("input[name='username']")
        self.password = page.locator("input[name='password']")
        self.login_button = page.locator("button:has-text('Login')")
```

### 7.2 新增業務流程
在 `scripts/` 新增流程腳本，例如：

```python
def login_success(page):
    lp = LoginPage(page)
    lp.username.fill("admin")
    lp.password.fill("password")
    lp.login_button.click()
```

### 7.3 新增測試
在 `testCase/` 新增測試案例：

```python
import pytest
from scripts.loginScript import login_success

@pytest.mark.demo
def test_login_success(browser_driver):
    login_success(browser_driver)
```

## 8. 優點與現階段限制

### 優點
- 架構簡單，容易理解
- 測試、頁面與流程分層清楚
- Playwright 真實瀏覽器操作
- 可透過 YAML 調整環境設定
- 執行後可自動產生 Allure HTML 報告

### 現階段限制
- 還沒有強化的 selector 管理層
- 沒有通用的頁面基底類別
- 沒有失敗自動截圖機制
- 目前仍是單一範例導向的框架骨架

## 9. 結論

這個專案目前更像一個「可擴充的自動化測試基礎骨架」，不是完整的企業級測試平台。它已經具備：
- 測試入口
- 測試 fixture
- Page Object
- 流程腳本
- 環境設定管理

未來若要繼續發展，可以再補強：
- 共用 `base_page.py`
- 環境切換與超時配置
- 失敗自動截圖（可整合進現有 Allure 報告的附件）
- 資料驅動測試
- CI/CD 整合

這樣可以逐步從目前的範例型架構，演進成適合實際團隊使用的自動化測試框架。
