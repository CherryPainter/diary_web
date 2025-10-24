import os
import subprocess

class AudioConverter:
    def __init__(self):
        """
        初始化，用户手动输入文件路径、格式和输出路径
        """
        self.input_path = self.get_input_path()
        self.output_format = self.get_output_format()
        self.output_dir = self.get_output_path()

    def get_input_path(self):
        """
        获取输入文件路径
        """
        while True:
            path = input("请输入要转换的音频文件路径（如 D:\\music\\example.mflac）: ").strip()
            if os.path.isfile(path):
                return path
            else:
                print("文件不存在，请重新输入！")

    def get_output_format(self):
        """
        选择输出格式
        """
        while True:
            format_choice = input("请选择输出格式（mp3 或 flac）: ").strip().lower()
            if format_choice in ["mp3", "flac"]:
                return format_choice
            else:
                print("格式无效，请重新输入！")

    def get_output_path(self):
        """
        获取输出目录
        """
        while True:
            path = input("请输入输出文件的保存目录（如 D:\\output\\）: ").strip()
            if not os.path.exists(path):
                os.makedirs(path)
                print(f"输出目录 {path} 不存在，已自动创建。")
            return path

    def convert(self):
        """
        执行音频文件转换
        """
        output_file = os.path.join(
            self.output_dir,
            f"{os.path.splitext(os.path.basename(self.input_path))[0]}.{self.output_format}"
        )

        print(f"\n正在转换文件：{self.input_path}")
        print(f"输出格式：{self.output_format}")
        print(f"保存路径：{output_file}")

        try:
            # 执行 FFmpeg 命令
            subprocess.run([
                "ffmpeg",
                "-i", self.input_path,       # 输入文件
                "-c:a", "libmp3lame" if self.output_format == "mp3" else "flac",  # 音频编码器
                "-b:a", "320k" if self.output_format == "mp3" else None,          # 比特率（MP3 专用）
                output_file
            ], check=True)

            print(f"\n转换成功！输出文件：{output_file}")
        except subprocess.CalledProcessError as e:
            print(f"\n转换失败：{e}")
        except FileNotFoundError:
            print("\n错误：未找到 FFmpeg，请确保已安装并配置环境变量！")

if __name__ == "__main__":
    print("欢迎使用音频转换工具！\n")
    converter = AudioConverter()
    converter.convert()