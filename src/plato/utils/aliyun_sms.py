import json
from dotenv import load_dotenv
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import logging
import os
load_dotenv()
# 配置你的阿里云短信服务相关信息
conf = {
    "accessKeyId": os.environ.get('accessKeyId'),
    "accessKeySecret": os.environ.get('accessKeySecret'),
    "signName": os.environ.get('北京零隙智能科技'),
    "templateCode": os.environ.get('SMS_295720915'),
}

# 初始化日志
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AliyunSMS:
    def __init__(self, access_key_id, access_key_secret, sign_name, template_code):
        self.client = AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
        self.sign_name = sign_name
        self.template_code = template_code

    def send_verify_code(self, v_code, phone):
        logger.info(f"Sending SMS code [{v_code}] to phone number: [{phone}]")

        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')  # https | http
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        request.add_query_param('RegionId', 'cn-hangzhou')
        request.add_query_param('PhoneNumbers', phone)
        request.add_query_param('SignName', self.sign_name)
        request.add_query_param('TemplateCode', self.template_code)
        request.add_query_param('TemplateParam', json.dumps({"code": v_code}))

        response = self.client.do_action_with_exception(request)
        response_dict = json.loads(response)

        if response_dict['Code'] == 'OK':
            logger.info(f"SMS sent successfully, response body [{response}]")
            return True
        else:
            logger.error(f"Failed to send SMS, response [{response}]")
            return False

# 创建一个实例
aliyun_sms = AliyunSMS(conf['accessKeyId'], conf['accessKeySecret'], conf['signName'], conf['templateCode'])
