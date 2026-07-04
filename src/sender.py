import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailSender:
    def __init__(self, config: dict = None):
        if config:
            self.config = config
        else:
            port_str = os.getenv('EMAIL_PORT', '587').strip()
            try:
                port = int(port_str)
            except ValueError:
                print(f"Invalid EMAIL_PORT: {port_str}, using default 587")
                port = 587

            self.config = {
                'from_addr': os.getenv('EMAIL_FROM'),
                'password': os.getenv('EMAIL_PASSWORD'),
                'to_addr': os.getenv('EMAIL_TO'),
                'server': os.getenv('EMAIL_SERVER', 'smtp.gmail.com'),
                'port': port
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
                html_lines.append(f'<h2>{line[3:]}</h2>')
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