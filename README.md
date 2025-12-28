# 简历优化工具

## 简介

本工具允许用户上传简历（PDF 格式）和输入职位描述，然后使用 AI 模型优化简历中的 "CORE COMPETENCIES" 部分，并生成新的 PDF 简历。

## 功能

*   上传简历（PDF 格式）
*   输入职位描述
*   使用 AI 模型优化简历
*   生成新的 PDF 简历
*   预览和下载优化后的简历

## 技术栈

*   前端：Vue.js
*   后端：FastAPI (Python)
*   PDF 处理：PyMuPDF, Reportlab
*   AI 模型：硅基流动大模型 API

## 依赖

*   前端：
    *   Vue.js
*   后端：
    *   FastAPI
    *   Uvicorn
    *   python-multipart
    *   PyMuPDF
    *   Reportlab
    *   requests
    *   python-dotenv

## 安装

1.  **克隆代码库：**

    ```bash
    git clone <代码库地址>
    cd app_cv
    ```

2.  **安装后端依赖：**

    ```bash
    cd backend
    pip install -r requirements.txt
    ```

3.  **安装前端依赖：**

    ```bash
    cd ../frontend
    npm install vue  # 确保安装 Vue.js
    ```

4.  **配置环境变量：**

    *   在 `backend/` 目录下创建一个 `.env` 文件，并添加硅基流动 API 密钥：

        ```
        SILICONFLOW_API_KEY=YOUR_API_KEY
        ```

        请替换 `YOUR_API_KEY` 为您的实际 API 密钥。您可以从 [硅基流动官网](https://siliconflow.cn/) 获取 API 密钥。

## 使用

1.  **运行后端：**

    ```bash
    cd backend
    uvicorn app:app --reload
    ```

2.  **运行前端：**

    ```bash
    cd frontend/public
    python3 -m http.server 3001
    ```
    然后在浏览器中访问：`http://localhost:3001/index.html`

3.  **API 访问：**

    *   **根路径**：`http://localhost:8000/` - API 信息和链接
    *   **API 文档**：`http://localhost:8000/docs` - 自动生成的 Swagger UI 文档
    *   **API 端点**：`http://localhost:8000/api/optimize` - 简历优化接口

4.  **使用流程：**

    *   在前端页面上传简历（PDF 格式）。
    *   在文本框中输入职位描述。
    *   点击 "生成优化简历" 按钮。
    *   如果生成成功，页面将显示优化后的简历预览，并提供下载链接。

## 注意事项

*   请确保已安装所有依赖，并配置了正确的 API 密钥。
*   本工具仅优化简历中的 "CORE COMPETENCIES" 部分，其他部分保持不变。
*   生成的 PDF 简历可能需要根据实际情况进行调整。

## 贡献

欢迎提交 issue 和 pull request，共同完善本工具。

## 许可证

MIT