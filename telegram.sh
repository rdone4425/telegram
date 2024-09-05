#!/bin/bash

# 定义GitHub仓库的URL
GITHUB_REPO_URL="https://github.com/rdone4425/telegram"

# 定义下载文件的保存路径（绝对路径）
SAVE_DIR="/root/telagram"

# 检查并安装Git
install_git() {
    if ! command -v git &> /dev/null; then
        echo "Git未安装，正在安装Git..."
        if sudo apt-get update && sudo apt-get install -y git; then
            echo "Git已成功安装"
        else
            echo "安装Git时出错，请检查系统安装源。"
            exit 1
        fi
    fi
}

# 检查并安装Python3
install_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Python未安装，正在安装Python..."
        if sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv; then
            echo "Python已成功安装"
        else
            echo "安装Python时出错，请检查系统安装源。"
            exit 1
        fi
    fi
}

# 创建保存目录
create_save_dir() {
    if [ -d "${SAVE_DIR}" ]; then
        echo "目录 ${SAVE_DIR} 已存在，将删除并重新创建。"
        rm -rf "${SAVE_DIR}"
    fi
    mkdir -p "${SAVE_DIR}"
    if [ $? -ne 0 ]; then
        echo "创建目录 ${SAVE_DIR} 时出错，请检查目录权限。"
        exit 1
    fi
}

# 克隆仓库
clone_repo() {
    if git clone "${GITHUB_REPO_URL}.git" "${SAVE_DIR}"; then
        echo "仓库已成功下载到 ${SAVE_DIR}"
    else
        echo "克隆仓库时出错，请检查URL和目录权限。"
        exit 1
    fi
}

# 进入保存目录
enter_save_dir() {
    cd "${SAVE_DIR}"
    if [ $? -ne 0 ]; then
        echo "进入目录 ${SAVE_DIR} 时出错，请检查目录路径。"
        exit 1
    fi
}

# 创建并激活虚拟环境
create_activate_venv() {
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "创建虚拟环境时出错，请检查Python安装。"
        exit 1
    fi
    source venv/bin/activate
}

# 安装依赖库
install_dependencies() {
    if pip install -r requirements.txt; then
        echo "所有依赖库已成功安装"
    else
        echo "安装依赖库时出错，请检查requirements.txt文件。"
        exit 1
    fi
}

# 运行telegram.py脚本
run_script() {
    if python3 telegram.py; then
        echo "telegram.py脚本已成功运行"
    else
        echo "运行telegram.py脚本时出错，请检查脚本文件。"
        exit 1
    fi
}

# 删除重复的telegram.sh脚本
remove_duplicate_scripts() {
    duplicate_scripts=$(find /root -maxdepth 1 -name "telegram.sh" | wc -l)
    if [ "$duplicate_scripts" -gt 1 ]; then
        echo "检测到多个telegram.sh脚本，将删除重复的脚本。"
        find /root -maxdepth 1 -name "telegram.sh" -not -path "/root/telegram.sh" -exec rm -f {} \;
        echo "重复的telegram.sh脚本已删除。"
    fi
}

# 主函数
main() {
    install_git
    install_python
    create_save_dir
    clone_repo
    enter_save_dir
    create_activate_venv
    install_dependencies
    run_script
    remove_duplicate_scripts
}

main
