
> 📌 **前置说明**：以下命令在 **Mac / Linux 终端** 或 **Windows的 Git Bash** 中完全通用。Windows用户如果用的是PowerShell/CMD，建议先安装Git for Windows [<sup>1</sup>](https://git-scm.com/download/win)，它会自带`Git Bash`，体验最接近标准教程。

---
### 🟢 第1步：打开终端
- **Mac**：`Command + 空格`输入 `Terminal` 回车
- **Windows**：`Win + S` 输入`Git Bash` 回车（推荐）或 `PowerShell`
- 输入以下命令确认进入你的主目录（看到类似`/Users/xxx`或`/c/Users/xxx`即可）：
```bash
cd ~
```

---
### 🔑 第2步：生成两套 SSH密钥
我们将生成两对密钥，分别命名为`id_github_a`（账号A）和 `id_github_b`（账号B）。

#### 1️⃣ 生成账号A的密钥
复制整行粘贴，回车：
```bash
ssh-keygen -t ed25519 -C "你的账号A邮箱" -f ~/.ssh/id_github_a
```
📝 **会出现提示，一律按 `Enter`键 3次**（不设置密码，方便开发）：
```
Generating public/private ed25519 key pair.
Enter file in which to save the key (~/.ssh/id_github_a): [直接回车]
Enter passphrase (empty for no passphrase): [直接回车]
Enter same passphrase again: [直接回车]
```
✅ 成功后会显示：`Your identification has been saved...`

#### 2️⃣ 生成账号B的密钥
同样操作，只改文件名和邮箱：
```bash
ssh-keygen -t ed25519 -C "你的账号B邮箱" -f ~/.ssh/id_github_b
```
同样按 3次`Enter`。

---
### 🌐 第3步：把“公钥”添加到 GitHub
Git 使用 `.pub` 结尾的**公钥**去 GitHub认门，**私钥绝对不要泄露**。

#### 1️⃣ 复制账号A的公钥
```bash
cat ~/.ssh/id_github_a.pub
```
终端会输出一串以`ssh-ed25519 AAAA... 你的邮箱` 开头的长字符串。**鼠标全选 → 复制**。

#### 2️⃣ 粘贴到GitHub
1. 浏览器打开[<sup>2</sup>](https://github.com/settings/keys)（用账号A登录）
2. 点击右上角`New SSH key`
3. `Title` 填`电脑名-账号A`（如`MacBook-A`），方便以后辨认
4. `Key` 粘贴刚才复制的内容
5. 点击`Add SSH key`（可能需要输密码）

#### 3️⃣ 重复以上步骤添加账号B
```bash
cat ~/.ssh/id_github_b.pub
```
复制后，**切换到账号B登录** GitHub，重复粘贴添加步骤。

---
### 🗺️ 第4步：配置 SSH路由规则（让电脑知道用哪把钥匙）
告诉Git：当访问 `github-a` 时用钥匙A，访问 `github-b` 时用钥匙B。

1. 创建/编辑配置文件：
```bash
# Windows记事本
notepad ~/.ssh/config
# 或 Mac/Linux 终端编辑器
nano ~/.ssh/config
```
2. 粘贴以下内容（**注意替换`github-a`/`github-b` 只是别名，不要改其他单词**）：
```ssh-config
Host github-a
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_github_a
    IdentitiesOnly yes

Host github-b
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_github_b
    IdentitiesOnly yes
```
3. 保存并关闭。
   - `notepad`：`Ctrl+S` 保存，关窗口
   - `nano`：`Ctrl+O` → 回车 → `Ctrl+X`

> ⚠️ **Mac/Linux 用户额外执行一句权限修复**：`chmod 600 ~/.ssh/config`

---
### 🤖 第5步：配置Git 自动识别Commit 身份
我们让Git根据**仓库所在文件夹**自动填入正确的名字和邮箱。

#### 1️⃣ 创建两个身份配置文件
```bash
# 创建账号A的配置
echo -e "[user]\n    name = 账号A显示名\n    email = 账号A邮箱" > ~/.gitconfig_a

# 创建账号B的配置
echo -e "[user]\n    name = 账号B显示名\n    email = 账号B邮箱" > ~/.gitconfig_b
```
> 💡 把 `账号A显示名` 和`账号A邮箱` 替换成你真实的。

#### 2️⃣ 写入全局路由规则
```bash
cat >> ~/.gitconfig << 'EOF'
[includeIf "gitdir:~/code/work/"]
    path = ~/.gitconfig_a
[includeIf "gitdir:~/code/personal/"]
    path = ~/.gitconfig_b
EOF
```
> 📌 **关键规则**：以后你的项目必须放在对应文件夹下：
> - 工作/账号A 的项目放：`~/code/work/`（Windows即`C:\Users\你的用户名\code\work\`）
> - 个人/账号B的项目放：`~/code/personal/`

---
### ✅ 第6步：验证 & 开始使用
#### 1️⃣ 测试 SSH连通性
```bash
ssh -T git@github-a
ssh -T git@github-b
```
✅ 正常返回：`Hi 你的账号A! You've successfully authenticated...`
✅ 正常返回：`Hi 你的账号B! You've successfully authenticated...`

#### 2️⃣ 克隆仓库测试
```bash
# 克隆账号A的仓库
cd ~/code/work
git clone git@github-a:你的A用户名/仓库名.git

# 克隆账号B的仓库
cd ~/code/personal
git clone git@github-b:你的B用户名/仓库名.git
```

#### 3️⃣ 用VS Code 打开
- 打开 VS Code → `文件` → `打开文件夹` → 选择刚才克隆的目录
- 随便改个文件，点击左侧源代码管理图标 → 提交 → 推送
- **全程不会弹窗问账号密码，Git 会自动使用对应身份**

---
### 🆘 小白常见报错急救包
| 报错现象 | 原因 | 解决 |
|----------|------|------|
| `Permission denied (publickey)` | SSH密钥没加对，或`~/.ssh/config` 拼写错误 | 检查GitHub是否粘贴了`.pub`文件内容；检查`config`里`IdentityFile`路径是否正确 |
| `Could not resolve hostname github-a` | `Host`别名拼错或没加`HostName github.com` | 严格对照第4步的`config`内容 |
| 提交后GitHub 显示`unknown user` | `includeIf` 路径没匹配上，或局部配置覆盖了全局 | 在项目里执行`git config user.email`看输出；确认仓库确实在 `~/code/work/` 或`personal/`下 |
| Windows 提示`Permissions for '~/.ssh/config' are too open` | 权限太开放 | 在 Git Bash执行：`chmod 600 ~/.ssh/config` |
