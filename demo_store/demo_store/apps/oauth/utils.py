import json
import urllib

from urllib.parse import urlencode, parse_qs
import logging
from urllib.request import urlopen
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings
from . import constants
from .exceptions import OAuthQQAPIError
logger = logging.getLogger('django')


class OAuthQQ(object):
    """qq认证辅助工具"""
    def __init__(self,client_id=None, client_secret=None, redirect_uri=None,state=None):
        self.client_id=client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

    def get_qq_login_url(self):
        """
        获取qq登录的网站
        :return: url网址
        """

        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }

        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)
        return url

    def get_access_token(self, code):
        """
        获取access_token
        :param code: qq提供的code
        :return: access_token
        """
        url = "https://graph.qq.com/oauth2.0/token?"
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }
        url+= urllib.parse.urlencode(params)
        try:
            # 发送请求
            resp = urlopen(url)
            # 读取响应体数据
            resp_data = resp.read()
            resp_data = resp_data.decode()
            #　解析access token
            resp_dict = urllib.parse.parse_qs(resp_data)
        except Exception as e:
            logger.error("获取access_token异常：%s"%e)
            raise OAuthQQAPIError
        else:
            access_token = resp_dict.get('access_token')

            return access_token[0]




    def get_openid(self, access_token):
        """
        获取用户的openid
        :param access_token: qq提供的access_token
        :return: open_id
        """
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        try:
            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            resp = urlopen(url)
            resp_data = resp.read().decode()

            resp_data = resp_data[10:-4]
            resp_dict = json.loads(resp_data)

        except Exception as e:

            logger.error('获取openid错误：%s' % e)

            raise OAuthQQAPIError
        else:
            openid = resp_dict.get('openid')
            return openid


    def generate_bind_user_access_token(self,openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: tokenf
        """
        serializer = TJWSSerializer(settings.SECRET_KEY,constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        token = serializer.dumps({"openid":openid})
        return token.decode()