def validate_email(email):
    # 1 长度判断 + 首（u/U）尾（ @hust.edu.cn）判断
    if len(email) == 22 and email.startswith(("U", "u")) and email.endswith("@hust.edu.cn"):
        # 2 拆分字符串 判断数字部分（[1:10]）是否在（1988-2020之间）
        # 热知识：1988年改名华中理工，又2000年改名华中科技时英文名不变，故该域名应该是自1988级的校友都可以使用（？
        if int(email[1:10]) in range(198800000, 202100000):
            return True
    return False


