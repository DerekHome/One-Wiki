# 初始化字段与默认数据

本文档说明 One WIKI 在空数据库首次启动时会创建的表结构、默认账号、默认群组和默认知识数据。

初始化入口位于 `server/app/main.py` 的 `lifespan` 启动逻辑中。后端启动时会先执行 `Base.metadata.create_all(bind=engine)` 创建缺失的数据表，然后按需补齐默认数据。

## 数据库连接

默认数据库连接：

```text
mysql+pymysql://onewiki:onewiki_dev_password@127.0.0.1:3306/onewiki?charset=utf8mb4
```

优先级：

1. 环境变量 `DATABASE_URL`
2. 设置中心保存的 `database_url`
3. 默认 MySQL 连接

测试环境或轻量开发环境可以显式传入 SQLite 连接，但正式默认目标是 MySQL。

## 初始化表结构

### users

用户账号表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 用户 UUID，主键 |
| `email` | String(255) | 登录邮箱，唯一索引 |
| `password_hash` | String(512) | 密码哈希 |
| `display_name` | String(120) | 显示名称 |
| `role` | String(32) | 角色，默认 `reader` |
| `is_active` | Boolean | 是否启用，默认 `true` |
| `created_at` | DateTime | 创建时间 |

### groups

用户群组表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 群组 UUID，主键 |
| `name` | String(120) | 群组名称，唯一索引 |
| `description` | Text | 群组说明 |
| `can_edit` | Boolean | 是否具备内容编辑能力 |
| `created_at` | DateTime | 创建时间 |

### group_members

用户与群组关系表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `group_id` | String(36) | 群组 ID，联合主键 |
| `user_id` | String(36) | 用户 ID，联合主键 |
| `created_at` | DateTime | 加入时间 |

### group_permissions

群组权限表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `group_id` | String(36) | 群组 ID，联合主键 |
| `permission` | String(80) | 权限编码，联合主键 |
| `created_at` | DateTime | 创建时间 |

### session_tokens

登录会话表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 会话 UUID，主键 |
| `token_hash` | String(64) | 会话 Token 哈希，唯一索引 |
| `user_id` | String(36) | 用户 ID |
| `expires_at` | DateTime | 过期时间 |
| `created_at` | DateTime | 创建时间 |

### topics

知识目录表，支持父子目录。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 目录 UUID，主键 |
| `parent_id` | String(36) | 父目录 ID，可为空 |
| `name` | String(120) | 目录名称，唯一 |
| `slug` | String(140) | 目录路径标识，唯一索引 |
| `description` | Text | 目录说明 |
| `sort_order` | Integer | 排序值 |
| `created_at` | DateTime | 创建时间 |

### knowledge_pages

知识正文表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 知识 UUID，主键 |
| `slug` | String(180) | 知识路径标识，唯一索引 |
| `title` | String(255) | 标题 |
| `summary` | Text | 摘要 |
| `content` | Text | 正文 |
| `status` | String(32) | 状态，默认 `draft` |
| `topic_id` | String(36) | 所属目录 ID |
| `owner_id` | String(36) | 创建人 ID |
| `current_version` | Integer | 当前版本号 |
| `review_at` | DateTime | 复核时间，可为空 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

### page_versions

知识版本表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 版本 UUID，主键 |
| `page_id` | String(36) | 知识 ID |
| `version_no` | Integer | 版本号 |
| `title` | String(255) | 版本标题 |
| `summary` | Text | 版本摘要 |
| `content` | Text | 版本正文 |
| `change_note` | Text | 变更说明 |
| `created_by` | String(36) | 创建人 ID |
| `created_at` | DateTime | 创建时间 |

`page_id + version_no` 唯一。

### tags

标签表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 标签 UUID，主键 |
| `name` | String(80) | 标签名称，唯一索引 |
| `created_at` | DateTime | 创建时间 |

### page_tags

知识与标签关系表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `page_id` | String(36) | 知识 ID，联合主键 |
| `tag_id` | String(36) | 标签 ID，联合主键 |

### favorites

用户收藏表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `user_id` | String(36) | 用户 ID，联合主键 |
| `page_id` | String(36) | 知识 ID，联合主键 |
| `created_at` | DateTime | 收藏时间 |

### file_assets

附件表。

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | String(36) | 附件 UUID，主键 |
| `storage_key` | String(512) | 存储键，唯一 |
| `original_name` | String(512) | 原始文件名 |
| `content_type` | String(255) | MIME 类型 |
| `size` | Integer | 文件大小 |
| `sha256` | String(64) | 文件 SHA-256 |
| `uploaded_by` | String(36) | 上传人 ID |
| `page_id` | String(36) | 关联知识 ID，可为空 |
| `created_at` | DateTime | 上传时间 |

## 默认初始化数据

### 默认管理员

仅当 `users` 表中不存在 `admin@example.com` 时创建。

| 字段 | 默认值 |
| --- | --- |
| `email` | `admin@example.com` |
| `password` | `ChangeMe123!` |
| `display_name` | `系统管理员` |
| `role` | `admin` |
| `is_active` | `true` |

首次登录后应立即修改默认密码。

### 默认群组

仅当同名群组不存在时创建。

| 群组 | 说明 | 权限 |
| --- | --- | --- |
| `Readers` | 只读用户 | 无编辑权限 |
| `Editors` | 可创建和编辑知识的用户 | `content.edit` |

默认管理员会自动加入 `Editors` 群组。

### 默认目录

仅当 `topics` 表为空时创建。

| 名称 | slug | 排序 | 说明 |
| --- | --- | --- | --- |
| 产品知识 | `product` | `1` | 产品、能力与使用方式 |
| 业务知识 | `business` | `2` | 业务方法与实践 |
| 方法与工具 | `methods` | `3` | 通用方法、工具与模板 |

### 默认欢迎页

仅当 `knowledge_pages` 表为空时创建。

| 字段 | 默认值 |
| --- | --- |
| `slug` | `welcome` |
| `title` | `欢迎来到智识库` |
| `status` | `published` |
| `current_version` | `1` |
| `topic_id` | 默认排序第一的目录 |
| `owner_id` | 默认管理员 |

同时创建一条 `page_versions` 记录，版本号为 `1`。

## 权限编码

当前内置权限编码如下：

| 权限 | 说明 |
| --- | --- |
| `content.edit` | 编辑文档 |
| `content.delete` | 删除文档 |
| `users.manage` | 用户管理 |
| `groups.manage` | 群组管理 |
| `settings.view` | 进入设置中心 |
| `settings.configure` | 修改通用设置 |
| `database.configure` | 配置数据库 |
| `ai.configure` | 配置 AI 服务 |
| `audit.view` | 查看审计信息 |

`admin` 角色默认拥有全部权限。非管理员用户通过角色和群组权限叠加获得能力。

## 初始化注意事项

- 初始化逻辑是幂等的：已存在的数据不会重复创建。
- 切换数据库后，新库会重新初始化默认账号和欢迎页；旧库中的用户与知识不会自动迁移。
- MySQL 数据和附件目录需要一起备份。
- Docker 部署时需要备份 `mysql-data` 和 `knowledge-files` 两个卷。
- 本地 Windows 直连 MySQL 时，请确认 `DATABASE_URL` 与实际数据库账号密码一致。
