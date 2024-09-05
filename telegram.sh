#!/bin/bash

# 定义GitHub仓库的URL
GITHUB_REPO_URL="https://github.com/rdone4425/telegram"

# 定义下载文件的保存路径（绝对路径）
SAVE_DIR="/root/telagram"

# 创建保存目录
mkdir -p "${SAVE_DIR}"

# 检查目标目录是否为空
if [ -n "$(ls -A ${SAVE_DIR})" ]; then
    echo "目标目录 ${SAVE_DIR} 已存在且不为空。"
    read -p "是否删除现有目录并继续？(y/n): " confirm
    if [[ ${confirm} == [yY] || ${confirm} == [yY][eE][sS] ]]; then
        rm -rf "${SAVE_DIR}"
        mkdir -p "${SAVE_DIR}"
    else
        echo "操作已取消。"
        exit 1
    fi
fi

# 克隆仓库
if git clone "${GITHUB_REPO_URL}.git" "${SAVE_DIR}"; then
    echo "仓库已成功下载到 ${SAVE_DIR}"
else
    echo "克隆仓库时出错，请检查URL和目录权限。"
    exit 1
fi
