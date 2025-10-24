# 贡献指南

感谢您对日记Web应用项目的关注和支持！我们欢迎并感谢各种形式的贡献，无论是bug修复、功能开发还是文档改进。

## 行为准则

参与本项目的所有贡献者都应该遵循开放、包容、尊重的原则。我们致力于提供一个友好、安全的环境，让所有参与者都能感到舒适。

## 开始贡献

### 开发流程

1. **Fork 仓库**
   在GitHub上点击"Fork"按钮，创建您自己的仓库副本。

2. **克隆仓库**
   ```bash
   git clone https://github.com/您的用户名/diary_web.git
   cd diary_web
   ```

3. **创建分支**
   为您的贡献创建一个新分支：
   ```bash
   git checkout -b feature/功能名称  # 功能开发
   或
   git checkout -b fix/bug修复描述  # Bug修复
   ```

4. **安装依赖**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # macOS/Linux
   pip install -r diary_app/requirements.txt
   ```

5. **配置开发环境**
   按照README.md中的说明配置`.env`文件。

6. **开发和测试**
   - 编写代码实现功能或修复bug
   - 确保编写单元测试
   - 运行测试确保所有功能正常

7. **提交更改**
   - 确保代码遵循项目的代码规范
   - 编写清晰、描述性的提交信息
   ```bash
   git add .
   git commit -m "简明扼要的描述：详细解释（如果需要）"
   ```

8. **推送到GitHub**
   ```bash
   git push origin 您的分支名称
   ```

9. **创建Pull Request**
   在GitHub上导航到您的仓库，点击"Pull request"按钮，填写详细信息。

## 代码规范

### Python代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 编码规范
- 使用四个空格进行缩进（不使用制表符）
- 每行不超过79个字符
- 类名使用驼峰命名法（CamelCase）
- 函数和变量名使用下划线分隔（snake_case）
- 常量使用全大写字母，下划线分隔
- 使用Type Hints提供类型信息

### 文档规范

- 所有公共函数、类和模块都应包含文档字符串
- 文档字符串使用Google风格：
  ```python
  def function_name(param1, param2):
      """函数功能的简短描述

      更详细的说明（如果需要）

      Args:
          param1: 参数1的说明
          param2: 参数2的说明

      Returns:
          返回值的说明

      Raises:
          可能抛出的异常说明
      """
      pass
  ```

### JavaScript代码规范

- 使用两个空格进行缩进
- 变量和函数名使用驼峰命名法（camelCase）
- 类名使用帕斯卡命名法（PascalCase）
- 使用ES6+语法

## 测试指南

### 运行测试

```bash
cd diary_app
python -m pytest
```

### 编写测试

- 为新功能编写单元测试
- 确保测试覆盖率尽可能高
- 测试应该是独立的，不依赖于外部资源

## 提交信息规范

提交信息应遵循以下格式：

```
<类型>: <简短描述>

<详细说明>（如果需要）

<相关issue或PR链接>（如果有）
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更改
- `style`: 代码风格更改（不影响功能）
- `refactor`: 代码重构（不添加功能，不修复bug）
- `test`: 测试相关更改
- `chore`: 构建过程或辅助工具的更改

## 问题报告

如果您发现bug或有新功能建议，请在GitHub上创建issue。提交issue时，请包含以下信息：

- 问题的简短描述
- 详细的问题重现步骤
- 预期行为和实际行为
- 环境信息（操作系统、Python版本等）
- 如果可能，提供错误日志或截图

## 代码审查

所有PR都将经过代码审查。请准备好回答问题并根据反馈进行修改。审查过程有助于保持代码质量和一致性。

## 联系方式

如有任何问题或需要帮助，请通过以下方式联系项目维护者：

- GitHub Issues: [Issues页面链接]

再次感谢您的贡献！