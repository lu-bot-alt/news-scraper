@echo off
:: 创建环境
conda env create -f environment.yml
:: 更新环境
conda env update -f environment.yml --prune
:: 清理缓存
conda clean --all -y