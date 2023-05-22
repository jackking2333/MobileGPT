import gradio as gr
import utils
from api import AutoAPI, get_openai_api_key
import os, shutil
import json
from autogpt.workspace import path_in_workspace
from PIL import Image
FILE_DIR = os.path.dirname(os.path.abspath(__file__))
# OUTPUT_DIR = os.path.join(os.path.dirname(FILE_DIR), "auto_gpt_workspace")
# 修改
OUTPUT_DIR = os.path.join(os.path.dirname(FILE_DIR), "mobile_gpt_workspace")
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
"""
CSS = 
# #chatbot {font-family: monospace;}
# #files .generating {display: none;}
# #files .min {min-height: 0px;}
"""
CSS = "footer {visibility:hidden}"
print(os.getenv("OPENAI_API_KEY"))
with gr.Blocks(css=CSS, title='中国移动智能对话平台') as app:
    with gr.Column() as setup_pane:
        gr.Markdown(f"""# Mobile-GPT
        中国移动智能对话平台
        """)
        # open_ai_key = os.getenv("OPENAI_API_KEY")
        with gr.Row():
            # open_ai_key = os.getenv("OPENAI_API_KEY")
            open_ai_key = gr.Textbox(
                value=get_openai_api_key(),
                label="OpenAI API Key",
                type="password",
                visible=False
            )
        gr.Markdown(
            "请根据提示填写以下内容，全部填写完成后点击‘开始’按钮即可开始对话。如果您对此过程不清晰，下面有几个例子可供参考。"
        )
        with gr.Row():
            ai_name = gr.Textbox(label="AI 名称", placeholder="例如：企业家-GPT")
            ai_role = gr.Textbox(
                label="AI 职责",
                placeholder="例如：一个旨在自主开发和经营业务的人工智能，其唯一目标是增加你的净资产。",
            )
        top_5_goals = gr.Dataframe(
            row_count=(5, "fixed"),
            col_count=(1, "fixed"),
            headers=["AI 目标 - 最多5个"],
            type="array"
        )
        start_btn = gr.Button("开始", variant="primary")
        with open(os.path.join(FILE_DIR, "examples.json"), "r") as f:
            example_values = json.load(f)
        gr.Examples(
            example_values,
            [ai_name, ai_role, top_5_goals],
            label='例子'
        )
    with gr.Column(visible=False) as main_pane:
        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(elem_id="chatbot", label="对话机器人")
                with gr.Row():
                    yes_btn = gr.Button("继续", variant="primary", interactive=False)
                    consecutive_yes = gr.Slider(
                        1, 10, 1, step=1, label="连续执行命令", interactive=False
                    )
                custom_response = gr.Textbox(
                    label="用户反馈",
                    placeholder="按回车提交",
                    interactive=False,
                )
            with gr.Column(scale=1):
                gr.HTML(
                    lambda: f"""
                        文件列表
                        <pre><code style='overflow-x: auto'>{utils.format_directory(OUTPUT_DIR)}</pre></code>
                """, every=3, elem_id="files"
                )
                download_btn = gr.Button("下载所有文件")
                upload_image = gr.Image(type="pil", label="上传图片")
                upload_button = gr.Button(value="上传您的图片", interactive=True, variant="primary")
                show_image = gr.Image(type="pil",show_label=True,label="生成图片")
                show_button = gr.Button(value="展示生成图片", interactive=True, variant="primary")

    chat_history = gr.State([[None, None]])
    api = gr.State(None)

    def start(open_ai_key, ai_name, ai_role, top_5_goals):
        auto_api = AutoAPI(open_ai_key, ai_name, ai_role, top_5_goals)
        return gr.Column.update(visible=False), gr.Column.update(visible=True), auto_api

    def bot_response(chat, api):
        messages = []
        for message in api.get_chatbot_response():
            messages.append(message)
            chat[-1][1] = "\n".join(messages) + "..."
            yield chat
        chat[-1][1] = "\n".join(messages)
        yield chat

    def send_message(count, chat, api, message="Y"):
        if message != "Y":
            count = 1
        for i in range(count):
            chat.append([message, None])
            yield chat, count - i
            api.send_message(message)
            for updated_chat in bot_response(chat, api):
                yield updated_chat, count - i

    def activate_inputs():
        return {
            yes_btn: gr.Button.update(interactive=True),
            consecutive_yes: gr.Slider.update(interactive=True),
            custom_response: gr.Textbox.update(interactive=True),
        }

    def deactivate_inputs():
        return {
            yes_btn: gr.Button.update(interactive=False),
            consecutive_yes: gr.Slider.update(interactive=False),
            custom_response: gr.Textbox.update(interactive=False),
        }
    def upload_img(gr_img):
        if gr_img is None:
            return None
        filename = 'upload.jpg'
        # save_path = path_in_workspace(filename)
        save_path = '/home/public/pj/Project/Mobile-GPT/mobile_gpt_workspace/' + filename
        gr_img.save(save_path)
        return gr.update(interactive=False),gr.update(value="上传完成", interactive=False)
    def show_img(gr_img):
        filename = 'generate.jpg'
        # generate_path = path_in_workspace(filename)
        generate_path = '/home/public/pj/Project/Mobile-GPT/mobile_gpt_workspace/'+filename
        return Image.open(generate_path),gr.update(value="刷新", interactive=True)
    start_btn.click(
        start,
        [open_ai_key, ai_name, ai_role, top_5_goals],
        [setup_pane, main_pane, api],
    ).then(bot_response, [chat_history, api], chatbot).then(
        activate_inputs, None, [yes_btn, consecutive_yes, custom_response]
    )

    yes_btn.click(
        deactivate_inputs, None, [yes_btn, consecutive_yes, custom_response]
    ).then(
        send_message, [consecutive_yes, chat_history, api], [chatbot, consecutive_yes]
    ).then(
        activate_inputs, None, [yes_btn, consecutive_yes, custom_response]
    )
    custom_response.submit(
        deactivate_inputs, None, [yes_btn, consecutive_yes, custom_response]
    ).then(
        send_message,
        [consecutive_yes, chat_history, api, custom_response],
        [chatbot, consecutive_yes],
    ).then(
        activate_inputs, None, [yes_btn, consecutive_yes, custom_response]
    )
    upload_button.click(upload_img, [upload_image], [upload_image, upload_button])
    show_button.click(show_img, [show_image], [show_image, show_button])

    def download_all_files():
        shutil.make_archive("outputs", "zip", OUTPUT_DIR)

    download_btn.click(download_all_files).then(None, _js=utils.DOWNLOAD_OUTPUTS_JS)

app.queue(concurrency_count=20).launch(file_directories=[OUTPUT_DIR], favicon_path='logo.png')
