#!/bin/bash

# 定义GitHub仓库的URL
GITHUB_REPO_URL="https://github.com/rdone4425/telegram"

# 定义下载文件的保存路径（绝对路径）
SAVE_DIR="/root/telagram"

# 定义压缩包的下载URL
ZIP_URL="${GITHUB_REPO_URL}/archive/master.zip"

# 检查并安装wget
if ! command -v wget &> /dev/null; then
    echo "wget未安装，正在安装wget..."
    if sudo apt-get update && sudo apt-get install -y wget; then
        echo "wget已成功安装"
    else
        echo "安装wget时出错，请检查系统安装源。"
        exit 1
    fi
fi

# 检查并安装unzip
if ! command -v unzip &> /dev/null; then
    echo "unzip未安装，正在安装unzip..."
    if sudo apt-get update && sudo apt-get install -y unzip; then
        echo "unzip已成功安装"
    else
        echo "安装unzip时出错，请检查系统安装源。"
        exit 1
    fi
fi

# 检查并安装Python3
if ! command -v python3 &> /dev/null; then
    echo "Python未安装，正在安装Python..."
    if sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv; then
        echo "Python已成功安装"
    else
        echo "安装Python时出错，请检查系统安装源。"
        exit 1
    fi
fi

# 创建保存目录
mkdir -p "${SAVE_DIR}"

# 下载压缩包
if wget -O "${SAVE_DIR}/master.zip" "${ZIP_URL}"; then
    echo "压缩包已成功下载到 ${SAVE_DIR}"
else
    echo "下载压缩包时出错，请检查URL和目录权限。"
    exit 1
fi

# 解压压缩包
if unzip "${SAVE_DIR}/master.zip" -d "${SAVE_DIR}"; then
    echo "压缩包已成功解压到 ${SAVE_DIR}"
else
    echo "解压压缩包时出错，请检查压缩包文件。"
    exit 1
fi

# 进入解压后的目录
cd "${SAVE_DIR}/telegram-master"

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖库
if pip install -r requirements.txt; then
    echo "所有依赖库已成功安装"
else
    echo "安装依赖库时出错，请检查requirements.txt文件。"
    exit 1
fi

# 运行telegram.py脚本
if python3 telegram.py; then
    echo "telegram.py脚本已成功运行"
else
    echo "运行telegram.py脚本时出错，请检查脚本文件。"
    exit 1
fi
