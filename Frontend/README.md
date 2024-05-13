# vue-admin-template

## 这是一个RFID餐厅管理后台页面

该后台分为几个部分
一、详情页
详情页用于展示餐厅近期的营销状况
* 可以根据需要显示月、周、日的[盈利金额]
* 展示[热门菜品]，方便商家调整经营策略

二、管理页
2.1 菜品管理页
用于调整菜品价格、菜品rfid信息等

2.2 用户管理页
用于修改前端用户信息，包括用户名和电话号等

## Build Setup

```bash
# 克隆项目
git clone https://github.com/PanJiaChen/vue-admin-template.git

# 进入项目目录
cd vue-admin-template

# 安装依赖
npm install

# 建议不要直接使用 cnpm 安装以来，会有各种诡异的 bug。可以通过如下操作解决 npm 下载速度慢的问题
npm install --registry=https://registry.npm.taobao.org

# 启动服务
npm run dev
```

浏览器访问 [http://localhost:9528](http://localhost:9528)

## 发布

```bash
# 构建测试环境
npm run build:stage

# 构建生产环境
npm run build:prod
```