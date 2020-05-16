from selenium import webdriver
import time
import datetime
import winsound
import ctypes
import verification_code


# from PIL import Image
# import schedule


def initialize_operation(username, password, speed):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(chrome_options=options)
    # Refresh rate
    driver.implicitly_wait(speed)
    driver.get("https://shower.jiangnan.edu.cn/h5/meeting_signup_list.php")
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("pwd").send_keys(password)
    driver.find_element_by_class_name("loginbutton").click()
    driver.find_element_by_class_name("user_text").click()
    return driver


def save_code(driver, image_path):
    element = driver.find_element_by_id("vi")
    element.screenshot(image_path)


def ver_code(image_path):
    username = 'reacodes'
    password = 'ilovemm2020'
    # 软件ID
    appid = 10835
    # 软件密钥
    appkey = '463224f0749874416e76d5d1468d1193'
    # 图片文件
    filename = image_path
    # 验证码类型，# 例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。在此查询所有类型 http://www.yundama.com/price.html
    codetype = 1004
    # 超时时间，秒
    timeout = 60

    # 初始化
    yundama = verification_code.YDMHttp(username, password, appid, appkey)

    # 登陆云打码
    uid = yundama.login()
    # print('uid: %s' % uid)

    # 查询余额
    # balance = yundama.balance()
    # print('balance: %s' % balance)

    # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
    cid, result = yundama.decode(filename, codetype, timeout)
    # print('cid: %s, result: %s' % (cid, result))
    return result


def shower_order_last_time(username, password, speed):
    driver = initialize_operation(username, password, speed)
    order_elements = driver.find_elements_by_class_name("pui_btn pui_btn_do2 yuyue")

    while len(order_elements) == 0:

        start = time.time()

        driver.get("https://shower.jiangnan.edu.cn/h5/meeting_signup_list.php")
        time.sleep(0.5)
        driver.find_element_by_id("loadmore").click()

        order_elements = driver.find_elements_by_css_selector("[class='pui_btn pui_btn_do2 yuyue']")
        count = len(order_elements)
        if count != 0:
            order_elements[count - 1].click()
            winsound.PlaySound('alert', winsound.SND_ASYNC)
            ctypes.windll.user32.MessageBoxW(0, "已成功预约最晚可预约时段", "恭喜", 0x1000)
            driver.quit()
            return
        time.sleep(2)

        end = time.time()
        time_use = end - start
        print("刷新一次：" + str(time_use))
    driver.quit()


def shower_order_specify_time(username, password, speed, order_date, order_times):
    driver = initialize_operation(username, password, speed)
    time.sleep(0.5)
    # 南区
    driver.find_element_by_id("loc_name").click()
    # time.sleep(0.5)
    driver.find_element_by_id("loadmore").click()
    order_elements = driver.find_elements_by_css_selector("[class='pui_user_menu pui_clear']")

    order_date_times_operation = []
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    if order_date == "1":
        order_date_operation = today.strftime("%m月%d日") + str("南区浴室（男）")
    else:
        order_date_operation = tomorrow.strftime("%m月%d日") + str("南区浴室（男）")
    for order_time in order_times:
        order_date_time_operation = order_date_operation + order_time + str("点档")
        order_date_times_operation.append(order_date_time_operation)

    while True:
        start = time.time()

        driver.get("https://shower.jiangnan.edu.cn/h5/meeting_signup_list.php")
        time.sleep(spd)
        # 南区
        driver.find_element_by_id("loc_name").click()
        time.sleep(1)
        driver.find_element_by_id("loadmore").click()
        order_elements = driver.find_elements_by_css_selector("[class='pui_user_menu pui_clear']")

        for order_element in reversed(order_elements):
            can_order = order_element.find_elements_by_css_selector("[class='pui_btn pui_btn_do2 yuyue']")
            # 如果当前时间段不可预约，直接下一个时间段
            if len(can_order) == 0:
                continue

            # 获取当前时间段时间
            can_time = order_element.find_element_by_tag_name("h3").text
            can_time = can_time.split('\n')[1]

            # 如果当前时间段可预约，比较时间段与输入的时间段列表，是否有吻合的时间段
            for order_date_time_operation in reversed(order_date_times_operation):
                # 如果吻合，进行预约
                if can_time == order_date_time_operation:
                    can_order[0].click()
                    time.sleep(0.5)

                    print("开始识别验证码")
                    ver_code_start = time.time()
                    save_code(driver, 'code.png')
                    result = ver_code('code.png')
                    print("验证码结果：" + str(result))
                    driver.find_element_by_id("yzm").send_keys(result)
                    driver.find_element_by_xpath('//*[@class="layui-m-layerbtn"]/span[2]').click()

                    # 如果验证失败

                    ver_code_end = time.time()
                    ver_code_use = ver_code_end - ver_code_start
                    print("打码用时：" + str(ver_code_use))

                    winsound.PlaySound('alert', winsound.SND_ASYNC)
                    ctypes.windll.user32.MessageBoxW(0, "已成功预约 " + order_date_time_operation, "恭喜", 0x1000)
                    driver.quit()
                    return

        end = time.time()
        time_use = end - start
        print("刷新一次：" + str(time_use))
    driver.quit()


if __name__ == "__main__":
    user = input("学号：")
    pwd = input("密码：")
    spd = float(input("速度："))

    want_date = input("预约日期，今天输入1，明天输入2，为空则预约当前最晚可预约时段：")
    while want_date != str(1) and want_date != str(2) and want_date != "":
        print("请输入正确格式")
        want_date = input("预约日期，今天输入1，明天输入2，为空则预约当前最晚可预约时段：")

    if want_date != "":
        want_time = input("预约时间，24小时制，用空格隔开多个时间：")
        while want_time == "":
            print("请输入正确格式")
            want_time = input("预约时间，24小时制，用空格隔开多个时间：")

        want_time_list = want_time.split()
        shower_order_specify_time(user, pwd, spd, want_date, want_time_list)
    else:
        shower_order_last_time(user, pwd, spd)

    # print("Starts on time at 12 o'clock")
    # schedule.every().day.at("12:00").do(shower_order, user, pwd)
