#!/bin/bash

# 定义GitHub仓库的URL
GITHUB_REPO_URL="https://github.com/rdone4425/telegram"

# 定义下载文件的保存路径（绝对路径）
SAVE_DIR="/root/telagram"

# 创建保存目录
mkdir -p "${SAVE_DIR}"

# 检查git命令是否成功执行
if git clone "${GITHUB_REPO_URL}.git" "${SAVE_DIR}"; then
    echo "仓库已成功下载到 ${SAVE_DIR}"
else
    echo "克隆仓库时出错，请检查URL和目录权限。"
    exit 1
fi
