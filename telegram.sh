#!/bin/bash

# 定义GitHub仓库的URL
GITHUB_REPO_URL="https://github.com/rdone4425/telegram"

# 定义下载文件的保存路径（绝对路径）
SAVE_DIR="/root/telagram"

# 创建保存目录
mkdir -p "${SAVE_DIR}"

# 使用git命令克隆整个仓库
git clone "${GITHUB_REPO_URL}.git" "${SAVE_DIR}"

echo "仓库已下载到 ${SAVE_DIR}"

# 赋予自身执行权限
chmod +x "${0}"

# 以root用户身份运行脚本
sudo "${0}"
