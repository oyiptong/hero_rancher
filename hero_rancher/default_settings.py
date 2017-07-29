import os
from Crypto.Protocol.KDF import PBKDF2

server = {
    "preferred_url_scheme": "http",
    "server_name": "127.0.0.1:5000",
    "debug": True,
    "dev_mode_counts": True,
    "profiler": False,
    "environment": "dev",
    "secret_key": "AjfG7KuAV+G3@LyfaRJbEATqRkUcbc",
    "template_dir": os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "templates"),
    "static_dir": os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "static"),
    "security": {
        "SECURITY_PASSWORD_HASH": "bcrypt",
        "SECURITY_PASSWORD_SALT": "FoU6SZq9w*at6eq@y&ZH@mmj*42giG",
        "SECURITY_CONFIRMABLE": False,
        "SECURITY_REGISTERABLE": False,
        "SECURITY_RECOVERABLE": True,
        "SECURITY_CHANGEABLE": True,
        "SECURITY_TRACKABLE": True,
        "SECURITY_DEFAULT_REMEMBER_ME": True,
        "SECURITY_LOGIN_SALT": "o,nNBe&WpaaWnCtbgPMwbCEPH8X8bW",
        "SECURITY_RESET_SALT": "8gvpJp$oz>BBaqLk2bxajvCJtEBhaf",
        "SECURITY_CONFIRM_SALT": "KrdQC,YJmWy6Ga;e8fxdWhDzxyeUJh",
        "SECURITY_REMEMBER_SALT": "EqUxjZ9MVasDV2nptaKsTA.&otECxK",
        "SECURITY_SEND_REGISTER_EMAIL": False,
        "SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL": True,
        "SECURITY_LOGIN_WITHOUT_CONFIRMATION": False,
        "WTF_CSRF_TIME_LIMIT": 31557600,
    },
    "encryption": {
        "AES_KEY": PBKDF2(
            password="gcuJsDka+Etp8>NzDQHdHkGiLRm4QH",
            salt=b'UfKqxzUG[U*XJfwFujz2smCCHNbn4d', dkLen=32, count=10000)
    }
}

py2neo = {
    "host": "localhost",
    "secure": False,
    "http_port": 7474,
    "https_port": 7473,
    "bolt": None,
    "bolt_port": 7687,
    "user": "neo4j",
    "password": "tTaFYzMNyvGKWGiZWJu4Hosr",
}
