import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def add_server_time(server_url="https://hub.weirdhost.xyz/server/6ba234bb"):
    """
    仅使用邮箱密码登录并点击 "시간추가" 按钮。
    """
    pterodactyl_email = os.environ.get('PTERODACTYL_EMAIL')
    pterodactyl_password = os.environ.get('PTERODACTYL_PASSWORD')

    if not (pterodactyl_email and pterodactyl_password):
        print("错误: 缺少登录凭据。请设置 PTERODACTYL_EMAIL 和 PTERODACTYL_PASSWORD 环境变量。")
        return False

    with sync_playwright() as p:
        # headless=True 适用于 GitHub Actions
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        page.set_default_timeout(60000)

        try:
            # 1. 访问登录页面
            login_url = "https://hub.weirdhost.xyz/auth/login"
            print(f"正在访问登录页面: {login_url}")
            page.goto(login_url, wait_until="networkidle")

            # 2. 填写登录表单
            # 考虑到可能是 React 应用，使用更通用的选择器
            email_selector = 'input[name="username"], input[type="text"]'
            password_selector = 'input[name="password"], input[type="password"]'
            # 使用你提供的 HTML 片段中的 "로그인" 文本作为定位符
            login_button_selector = 'button:has-text("로그인")'

            print("等待登录表单元素...")
            page.wait_for_selector(email_selector, state="visible")
            
            print("正在填写凭据...")
            page.fill(email_selector, pterodactyl_email)
            page.fill(password_selector, pterodactyl_password)

            print("点击登录按钮...")
            # 点击登录并等待页面跳转
            page.click(login_button_selector)
            
            # 等待跳转完成（不包含 login 字符串即视为成功）
            page.wait_for_function("!window.location.href.includes('login')", timeout=30000)

            if "login" in page.url:
                print("登录失败，页面未发生跳转。")
                page.screenshot(path="login_failed.png")
                browser.close()
                return False
            
            print("登录成功。")

            # 3. 访问目标服务器页面
            print(f"正在导航至服务器页面: {server_url}")
            page.goto(server_url, wait_until="networkidle")

            # 4. 查找并点击 "시간추가" 按钮
            add_button_selector = 'button:has-text("시간추가")'
            print(f"等待 '{add_button_selector}' 按钮出现...")

            try:
                add_button = page.locator(add_button_selector)
                add_button.wait_for(state='visible', timeout=30000)
                
                # 滚动到按钮位置并点击
                add_button.scroll_into_view_if_needed()
                add_button.click()
                
                print("成功点击 '시간추가' 按钮。")
                time.sleep(5)  # 等待操作生效
                print("任务完成。")
                browser.close()
                return True
            except PlaywrightTimeoutError:
                print("错误: 未能在页面上找到 '시간추가' 按钮。")
                page.screenshot(path="button_not_found.png")
                browser.close()
                return False

        except Exception as e:
            print(f"执行过程中发生异常: {str(e)}")
            page.screenshot(path="error_debug.png")
            browser.close()
            return False

if __name__ == "__main__":
    print("开始执行任务...")
    if add_server_time():
        print("脚本运行成功。")
        exit(0)
    else:
        print("脚本运行失败。")
        exit(1)
