import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def add_server_time(server_url="https://hub.weirdhost.xyz/server/6ba234bb"):
    pterodactyl_email = os.environ.get('PTERODACTYL_EMAIL')
    pterodactyl_password = os.environ.get('PTERODACTYL_PASSWORD')

    if not (pterodactyl_email and pterodactyl_password):
        print("错误: 缺少环境变量 PTERODACTYL_EMAIL 或 PTERODACTYL_PASSWORD")
        return False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 使用较大的视口确保元素都在可见范围内
        context = browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = context.new_page()
        page.set_default_timeout(60000)

        try:
            # 1. 访问登录页
            print("正在访问登录页面...")
            page.goto("https://hub.weirdhost.xyz/auth/login", wait_until="networkidle")

            email_selector = 'input[name="username"]'
            password_selector = 'input[name="password"]'
            # 针对你提供的 HTML 结构，使用包含特定文本的 label 里的 input
            agreement_checkbox = 'label:has-text("동의합니다") input[type="checkbox"]'
            login_button_selector = 'button:has-text("로그인")'

            # 2. 填写表单
            print("正在填写凭据...")
            page.wait_for_selector(email_selector)
            page.fill(email_selector, pterodactyl_email)
            page.fill(password_selector, pterodactyl_password)

            # 3. 核心步骤：勾选“14岁以上及同意条款”
            print("正在勾选同意协议复选框...")
            try:
                page.locator(agreement_checkbox).check()
                print("复选框已勾选。")
            except Exception as checkbox_err:
                print(f"勾选复选框时遇到问题（可能已默认勾选）: {checkbox_err}")

            # 4. 点击登录
            print("正在点击登录按钮...")
            page.click(login_button_selector, force=True)
            
            # 等待跳转或网络静默
            time.sleep(5) 

            # 5. 导航至目标服务器
            print(f"尝试导航至目标页面: {server_url}")
            page.goto(server_url, wait_until="networkidle")

            if "login" in page.url:
                print("登录失败：未能进入服务器页面。请检查账号密码及协议勾选是否生效。")
                page.screenshot(path="login_failed_after_check.png")
                return False

            # 6. 点击续期按钮
            add_button_selector = 'button:has-text("시간추가")'
            print(f"等待 '{add_button_selector}' 按钮出现...")
            
            add_button = page.locator(add_button_selector)
            add_button.wait_for(state='visible', timeout=30000)
            
            print("找到按钮，执行点击...")
            add_button.click()
            
            time.sleep(5)
            print("任务执行成功。")
            page.screenshot(path="success_result.png")
            
            browser.close()
            return True

        except Exception as e:
            print(f"发生异常: {str(e)}")
            page.screenshot(path="debug_error.png")
            browser.close()
            return False

if __name__ == "__main__":
    if add_server_time():
        print("脚本运行成功。")
        exit(0)
    else:
        print("脚本运行失败。")
        exit(1)
