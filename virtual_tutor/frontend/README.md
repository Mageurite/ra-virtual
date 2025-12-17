# 前端进度与运行说明（Virtual Mentor）

## 1. 概览
当前前端主要包含两条使用路径：
- **管理员端（Admin Portal）**：管理员登录后管理 Tutor/学生、查看日志等
- **学生端（Student Portal）**：学生通过 Tutor 专属 URL 登录并进入对话/Session 页面

前端通过 `/api/*` 路径与后端 REST API 交互。

---

## 2. 当前进度（截至今天）

### ✅ 已实现 / 可用
1. **管理员登录（Admin Login）已可用**
   - 接口：`POST /api/auth/login`
   - 请求类型：`application/x-www-form-urlencoded`
     - 字段：`username`、`password`
   - 成功后后端返回 `access_token`，前端存入：
     - `localStorage.token`
     - `localStorage.user`（包含 role/email 等信息）

2. **管理员路由与整体框架已跑通**
   - 默认入口会跳转到 `/admin/login`
   - 登录成功后进入 `/admin/*` 区域
   - 管理员主框架：`UserAdminPage`
     - 左侧：`AdminSidebar`
     - 右侧：根据 `selectedMenu` 渲染对应内容（目前由 `UserTable` 承载）

3. **Tutor 创建已可用**
   - 在管理员端界面上可以成功创建 Tutor
   - Tutor 列表页面可访问（是否展示/字段是否齐全取决于当前 `selectedMenu` 对应组件实现）

4. **学生端“专属 URL”路由结构已准备**
   - 学生登录路由：`/session/:tutorId/login`
   - 学生会话/聊天路由：`/session/:tutorId`
   - 学生登录与会话页面组件已准备，但仍需进一步与后端功能完整对齐/联调

---

## 3. 前端目录结构说明（当前项目）
主要目录：
- `src/components/*`：UI 组件（Admin/Student 都在这里）
- `src/services/*`：封装的 API 调用（auth/tutor/admin-student 等）
- `src/utils/request.js`：Axios 实例 + 拦截器（注入 token、统一错误处理等）
- `src/App.js`：React Router 路由与登录态判断
- `src/config.js`：后端地址等配置

说明：当前项目没有 `pages/` 文件夹，页面组件直接放在 `components/` 下。

---

## 4. 如何运行（开发/联调）

### 4.1 启动后端
确保后端已启动且可访问，例如：
- 后端地址：`http://127.0.0.1:8000`

快速测试管理员登录接口：
```bash
curl -i -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin123"
````

### 4.2 启动前端

进入 `frontend/` 目录：

```bash
npm install
npm start
```
如果无法启动，可以尝试

```bash
HOST=0.0.0.0 PORT=3000 \
DANGEROUSLY_DISABLE_HOST_CHECK=true \
WDS_SOCKET_HOST=51.161.130.234 WDS_SOCKET_PORT=3000 \
npm start
```

默认前端地址：

* `http://localhost:3000`

---

## 5. /api 请求与代理说明（非常重要）

前端 Axios 当前使用：

* `baseURL: "/api"`

这意味着浏览器会把请求发到：

* `http://<前端域名>/api/...`

要让它真正到达后端，需要满足以下之一：

1. **开发代理（dev proxy）**：把 `/api` 转发到后端（推荐）
2. **生产反向代理（Nginx/Express）**：在服务器上配置 `/api` 转发到后端服务

如果浏览器登录失败但 curl 成功：

* 打开 DevTools → Network
* 检查请求是否真的发到了后端（而不是被前端服务拦截/返回静态资源）

---

## 6. 登录态与 Token 行为

* Token 存储：

  * `localStorage.token`
  * `localStorage.user`（JSON 字符串）
* Axios 请求拦截器会在请求头自动附加：

  * `Authorization: Bearer <token>`（当 token 存在时）

---

## 7. 已知问题 / 待办事项（TODO）

1. **复制 Student Login URL 报错**
   * 在 HTTP / 非安全上下文时，`navigator.clipboard` 可能不可用
   * 后续需要加“降级方案”（如 `document.execCommand('copy')` 或提示手动复制）

2. **管理员侧边栏菜单与后端功能还未完全对齐**
* 需要进一步对齐 brief + 后端已有接口，例如：
    * Tutor 下的 Students（list/create/update）
    * Student Sessions / Messages（学生侧）
    * Audit Logs（管理员侧）
  * 下一步：明确每个菜单 key 对应的页面组件与 service，并完成联调

---

## 8. 快速自测清单

启动前后端后：

1. 打开：`http://<host>:3000/admin/login`
2. 用管理员账号登录
3. 在控制台确认：

   * `localStorage.getItem("token")` 不为 null
4. 打开 Tutors 页面，尝试创建 Tutor
5. 确认 Tutor 创建成功并能在列表中看到（若列表已接通）
6. （可选）打开 Swagger 文档，验证受保护接口需要 Bearer token
