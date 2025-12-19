import os
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def add_server_time():
    # 配置参数
    server_url = "https://hub.weirdhost.xyz/server/6ba234bb"
    login_url = "https://hub.weirdhost.xyz/auth/login"
    
    # 从环境变量获取账号密码
    email = os.environ.get('PTERODACTYL_EMAIL')
    password = os.environ.get('PTERODACTYL_PASSWORD')

    if not email or not password:
        print("错误: 请在 GitHub Secrets 中设置 PTERODACTYL_EMAIL 和 PTERODACTYL_PASSWORD")
        return False

    with sync_playwright() as p:
        # 启动浏览器，模拟真人的 User-Agent
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        
        # 设置全局超时为 60 秒
        page.set_default_timeout(60000)

        try:
            # 1. 访问登录页面
            print(f"正在打开登录页: {login_url}")
            page.goto(login_url, wait_until="networkidle")

            # 2. 填写表单
            # Pterodactyl 面板通常使用 name="username" 接收邮箱
            print("正在填写账号密码...")
            page.fill('input[name="username"]', email)
            page.fill('input[name="password"]', password)

            # 3. 点击登录按钮 (使用你提供的韩文元素定位)
            print("正在尝试点击登录按钮 (로그인)...")
            # 这里使用了包含 "로그인" 文字的按钮选择器
            login_btn = page.locator('button:has-text("로그인")')
            
            if login_btn.count() == 0:
                # 备用方案：如果还没切到韩文，尝试找常规的 Login 按钮
                login_btn = page.locator('button:has-text("Login")')

            login_btn.click()

            # 4. 等待跳转到后台
            print("正在等待登录跳转...")
            page.wait_for_load_state("networkidle")

            # 检查是否登录成功（URL 不应包含 auth/login）
            if "login" in page.url or "auth" in page.url:
                print("登录失败，页面仍留在登录页。可能是账号密码错误或触发了验证码。")
                page.screenshot(path="login_failed.png")
                return False
            
            print("登录成功，进入后台。")

            # 5. 直接跳转到服务器控制台
            print(f"正在进入服务器页面: {server_url}")
            page.goto(server_url, wait_until="networkidle")

            # 6. 点击“增加时间”按钮
            # 兼容韩文 "시간추가" 和中文 "增加时间"
            add_time_btn = page.locator('button:has-text("시간추가"), button:has-text("增加时间")')
            
            if add_time_btn.count() > 0:
                print("找到续期按钮，正在点击...")
                add_time_btn.first.click()
                time.sleep(3) # 等待服务器处理
                print("【成功】已点击增加时间按钮。")
                page.screenshot(path="success_result.png")
                return True
            else:
                print("未能找到续期按钮（시간추가），请检查服务器是否已过期或 URL 是否正确。")
                page.screenshot(path="button_not_found.png")
                return False

        except Exception as e:
            print(f"运行中发生异常: {e}")
            # 截图保存，方便你下载查看当时的页面状态
            page.screenshot(path="error_debug.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    print("=== 任务开始 ===")
    if add_server_time():
        print("=== 任务结束：成功 ===")
        exit(0)
    else:
        print("=== 任务结束：失败 ===")
        exit(1)
