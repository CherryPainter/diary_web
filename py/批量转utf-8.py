import os
from chardet import detect


class EncodingConverter:
    def __init__(self, input_dir, output_dir, target_encoding="utf-8", include_bom=False):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_encoding = target_encoding
        self.include_bom = include_bom

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def detect_encoding(self, file_path):
        """Detect the encoding of a file."""
        with open(file_path, 'rb') as file:
            raw_data = file.read()
        return detect(raw_data)['encoding']

    def convert_file(self, file_path):
        """Convert a single file to the target encoding."""
        encoding = self.detect_encoding(file_path)
        output_file_path = os.path.join(self.output_dir, os.path.basename(file_path))

        try:
            with open(file_path, 'r', encoding=encoding) as source_file:
                content = source_file.read()

            with open(output_file_path, 'w', encoding=self.target_encoding, newline='') as target_file:
                if self.include_bom and self.target_encoding.lower() == 'utf-8':
                    target_file.write('\ufeff')  # Write BOM
                target_file.write(content)

            print(f"Converted: {file_path} -> {output_file_path} (from {encoding} to {self.target_encoding})")
        except Exception as e:
            print(f"Error converting {file_path}: {e}")

    def convert_all_files(self):
        """Convert all text files in the input directory to the target encoding."""
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                input_file_path = os.path.join(root, file)
                self.convert_file(input_file_path)


if __name__ == "__main__":
    print("欢迎使用批量编码转换器!")
    input_dir = input("输入输入目录的路径： ").strip()
    output_dir = input("输入输出目录的路径： ").strip()
    target_encoding = input("输入目标编码（默认：utf-8）： ").strip() or "utf-8"
    include_bom = input("是否包含 UTF-8 文件的 BOM？（y/n，默认值：n）： ").strip().lower() == 'y'

    converter = EncodingConverter(input_dir, output_dir, target_encoding, include_bom)
    print("开始转换...")
    converter.convert_all_files()
    print("转换完成！")