"""Commands for converting image to text."""
import json

import requests

# from autogpt.commands.command import command
from autogpt.config import Config
from autogpt.workspace import path_in_workspace
from PIL import Image
import base64
import io
import deepl
auth_key = 'c4953a25-5ca7-3b65-c0bd-0823b102977d:fx'
translator = deepl.Translator(auth_key)
CFG = Config()


# @command(
#     "image_to_text",
#     "将图片转为文本",
#     '"文件名": "<filename>"',
#     True,
#     "Configure huggingface_image_to_text_model.",
# )
def image_to_text(prompt: str) -> str:
    if "生成" in prompt or "generate" in prompt or "upload" in prompt or "网络" in prompt or "画" in prompt:
        filename = 'generate.jpg'
    else:
        filename = 'upload.jpg'
    # 设置请求参数
    url = 'http://127.0.0.1:12345/predict'
    # filename = '/home/public/pj/Project/AutoGPT/AutoGPT-UI/image.jpg'
    filename = path_in_workspace(filename)
    image = Image.open(filename)
    image = image.convert('RGB')
    img_bytes = io.BytesIO()
    # 将图片数据存入字节流管道， format可以按照具体文件的格式填写
    image.save(img_bytes, format="JPEG")
    # 从字节流管道中获取二进制
    img_bytes = img_bytes.getvalue()

    # 将图像数据转换为base64编码的字符串
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    # 将图像数据包含在JSON对象中
    json_data = {"text": "图片描述", "image_data": img_base64}
    #发送带有参数的POST请求
    response = requests.post(url, data=json_data)
    answer = json.loads(response.text)["answer"]
    answer =  translator.translate_text(answer, target_lang='ZH')
    answer = answer.text
    # 输出响应结果
    return answer

