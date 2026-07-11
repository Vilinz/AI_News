import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


SMTP_CONFIGS = {
    'qq.com': {'server': 'smtp.qq.com', 'port': 465},
    '163.com': {'server': 'smtp.163.com', 'port': 465},
    '126.com': {'server': 'smtp.126.com', 'port': 465},
    'gmail.com': {'server': 'smtp.gmail.com', 'port': 587},
    'outlook.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
    'hotmail.com': {'server': 'smtp-mail.outlook.com', 'port': 587},
    'yahoo.com': {'server': 'smtp.mail.yahoo.com', 'port': 587},
}


def detect_smtp_config(email: str) -> dict:
    """根据邮箱后缀自动检测 SMTP 配置"""
    if not email:
        return {'server': 'smtp.gmail.com', 'port': 587}
    email = email.lower().strip()
    for domain, config in SMTP_CONFIGS.items():
        if email.endswith(f'@{domain}'):
            return config
    return {'server': 'smtp.gmail.com', 'port': 587}


class EmailSender:
    def __init__(self, config: dict = None):
        if config:
            self.config = config
        else:
            # 使用全局配置
            self.config = {
                'from_addr': config.email_from,
                'password': config.email_password,
                'to_addr': config.email_to,
                'server': config.email_server,
                'port': config.email_port
            }

        self._validate_config()

    def _validate_config(self):
        required = ['from_addr', 'password', 'to_addr', 'server', 'port']
        missing = [k for k in required if not self.config.get(k)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

    def send(self, subject: str, html_content: str, plain_text: str = None) -> bool:
        """发送邮件"""
        msg = MIMEMultipart('alternative')
        msg['From'] = self.config['from_addr']
        msg['To'] = self.config['to_addr']
        msg['Subject'] = subject

        # 添加纯文本和HTML内容
        if plain_text:
            msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        try:
            # 根据端口选择连接方式
            if self.config['port'] == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.config['server'], self.config['port'], context=context, timeout=10) as server:
                    server.login(self.config['from_addr'], self.config['password'])
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.config['server'], self.config['port'], timeout=10) as server:
                    server.starttls()
                    server.login(self.config['from_addr'], self.config['password'])
                    server.send_message(msg)
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def send_news(self, summary: str, date: str) -> bool:
        """发送每日新闻邮件"""
        subject = f"📅 每日科技简报 - {date}"

        # 简单的 HTML 包装
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h2 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
                h3 {{ color: #555; }}
                h4 {{ color: #e74c3c; border-bottom: 1px solid #f39c12; padding-bottom: 5px; }}  /* 今日头条使用红色 */
                h5 {{ color: #e74c3c; font-weight: bold; margin-top: 10px; }}  /* 子分类标题 */
                a {{ color: #4CAF50; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #888; }}
            </style>
        </head>
        <body>
            <h1>📬 每日科技简报</h1>
            <p>为您精选 {date} 的科技、AI 和开源项目热点。</p>
            {self._markdown_to_html(summary)}
            <div class="footer">
                <p>本邮件由 GitHub Actions 自动发送</p>
            </div>
        </body>
        </html>
        """

        return self.send(subject, html_content)

    def _markdown_to_html(self, text: str) -> str:
        """简单的 Markdown 到 HTML 转换"""
        lines = text.split('\n')
        html_lines = []
        in_list = False

        for line in lines:
            if line.startswith('## '):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                # 特殊处理今日头条章节
                if '今日头条' in line:
                    html_lines.append('<h4>今日头条</h4>')
                else:
                    html_lines.append(f'<h2>{line[3:]}</h2>')
            elif line.startswith('**') and line.endswith('**'):
                # 处理加粗文本（如：**科技热点**）
                content = line.strip('**')
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h5 style="color: #e74c3c; margin-top: 15px;">{content}</h5>')
            elif line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{line[2:]}</li>')
            elif line.startswith('-'):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{line[1:]}</li>')
            elif line.strip() == '':
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append('<br>')
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<p>{line}</p>')

        if in_list:
            html_lines.append('</ul>')

        return '\n'.join(html_lines)