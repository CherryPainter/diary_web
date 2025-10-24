from setuptools import setup, find_packages
import os

# 读取README.md作为项目描述
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# 读取requirements.txt文件获取依赖列表
with open(os.path.join(os.path.dirname(__file__), 'diary_app', 'requirements.txt'), 'r', encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='diary_web',
    version='1.0.0',
    description='一个基于Flask的个人日记Web应用',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='项目团队',
    author_email='sqy3258731070@163.com',
    url='https://github.com/CherryPainter/diary_web.git',  # 替换为实际的GitHub仓库URL
    packages=find_packages(),
    package_data={
        'diary_app': [
            'templates/**/*',
            'static/**/*',
            'requirements.txt'
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest==6.2.5',
            'pytest-flask==1.2.0',
            'coverage==6.2',
            'flake8==4.0.1',
            'black==22.3.0',
            'mypy==0.942',
        ],
    },
    entry_points={
        'console_scripts': [
            'diary-web=diary_app.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business :: News/Diary',
    ],
    python_requires='>=3.8',
    license='MIT',
    keywords='diary, flask, web-application, personal-journal',
)