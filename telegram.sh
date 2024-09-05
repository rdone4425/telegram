#!/bin/bash

# 定义GitHub仓库的URL
GITHUB_REPO_URL="https://github.com/rdone4425/telegram"

# 定义下载文件的保存路径（绝对路径）
SAVE_DIR="/root/telagram"

# 检查Git和Python是否已安装
if ! command -v git &> /dev/null; then
    echo "Git未安装，请先安装Git。"
    exit 1
fi

if ! command -v python &> /dev/null; then
    echo "Python未安装，请先安装Python。"
    exit 1
fi

# 创建保存目录
mkdir -p "${SAVE_DIR}"

# 克隆仓库
if git clone "${GITHUB_REPO_URL}.git" "${SAVE_DIR}"; then
    echo "仓库已成功下载到 ${SAVE_DIR}"
else
    echo "克隆仓库时出错，请检查URL和目录权限。"
    exit 1
fi

# 进入保存目录
cd "${SAVE_DIR}"

# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖库
if pip install -r requirements.txt; then
    echo "所有依赖库已成功安装"
else
    echo "安装依赖库时出错，请检查requirements.txt文件。"
    exit 1
fi

# 运行telegram.py脚本
if python telegram.py; then
    echo "telegram.py脚本已成功运行"
else
    echo "运行telegram.py脚本时出错，请检查脚本文件。"
    exit 1
fi
