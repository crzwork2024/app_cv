from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import requests
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from dotenv import load_dotenv
import logging
import time
from typing import Annotated

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径，重定向到 API 文档"""
    return {"message": "简历优化工具 API", "docs": "/docs", "api": "/api/optimize"}

# --- LLM API Configuration ---
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY")
SILICONFLOW_API_URL = "https://api.siliconflow.cn/v1/chat/completions"  # Renamed for clarity
SILICONFLOW_MODEL_ID = "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B"  # Renamed for clarity

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- LLM API Call Function ---
def _siliconflow_call(prompt: str) -> str:
    """Calls the SiliconFlow API with the given prompt."""
    logging.info(f"Entering _siliconflow_call with prompt: {prompt}")
    logging.info(f"Invoking SiliconFlow LLM with model: {SILICONFLOW_MODEL_ID}")
    start_time = time.time()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SILICONFLOW_API_KEY}"
    }
    payload = {
        "model": SILICONFLOW_MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": 10000
    }
    logging.info(f"Payload: {payload}")
    try:
        resp = requests.post(SILICONFLOW_API_URL, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        end_time = time.time()
        logging.info(f"SiliconFlow LLM call completed in {end_time - start_time:.2f} seconds.")
        response_json = resp.json()
        logging.info(f"Response JSON: {response_json}")
        result = response_json["choices"][0]["message"]["content"].strip()
        logging.info(f"Exiting _siliconflow_call with result: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"SiliconFlow API call failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM API error: {e}")

async def extract_pdf_text(pdf_file: UploadFile):
    logging.info("Entering extract_pdf_text")
    # 使用 pymupdf 提取PDF文本
    try:
        contents = await pdf_file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        text = ""
        for page in doc.pages():
            text += page.get_text()
        logging.info(f"Extracted text: {text}")
        logging.info("Exiting extract_pdf_text")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from PDF: {e}")
        raise HTTPException(status_code=500, detail=f"PDF extraction error: {e}")

def generate_pdf(resume_text: str):
    logging.info("Entering generate_pdf")
    # 使用 reportlab 生成新的PDF文件
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    text_object = c.beginText(40, 750)
    text_object.textLines(resume_text)
    c.drawText(text_object)
    c.showPage()
    c.save()
    buffer.seek(0)
    logging.info("Generated PDF in memory")
    logging.info("Exiting generate_pdf")
    return buffer

@app.post("/api/optimize")
async def optimize_resume(resume: UploadFile, jobDescription: Annotated[str, Form()]) -> StreamingResponse:
    logging.info("Entering optimize_resume")
    # 获取上传的文件和职位描述
    logging.info(f"Uploaded resume file: {resume.filename}")
    logging.info(f"Job description: {jobDescription}")

    # 提取简历文本
    try:
        old_resume_text = await extract_pdf_text(resume)
    except HTTPException as e:
        logging.error(f"PDF extraction failed: {e}")
        raise e
    logging.info(f"Old resume text: {old_resume_text}")

    # 提取 CORE COMPETENCIES 部分
    start = old_resume_text.find("CORE COMPETENCIES")
    end = old_resume_text.find("PERSONAL DETAILS")
    core_competencies = old_resume_text[start:end].strip()
    logging.info(f"Core competencies: {core_competencies}")

    # 将职位要求和核心竞争力部分传递给大模型API
    try:
        #prompt = f"请根据以下职位描述优化以下核心竞争力：\\n职位描述：{jobDescription}\\n核心竞争力：{core_competencies}"
        prompt = f"""请根据职位描述优化简历中的核心竞争力部分。
                要求：
                1. 保持客观事实：不要修改或添加不存在的技术栈、经验年限等客观信息
                2. 严格优化表达：不可以为了更好地匹配职位要求，随意编写不存在的技能
                3. 保持原有格式：每行直接陈述技术能力，不要添加"技能："等前缀
                4. 技术细节可以稍微强化，但不能编造不存在的能力
                5. 用英语回答，并最多给出 9 条建议，注意要严格遵守这条

                职位描述：{jobDescription}

                原始核心竞争力：
                {core_competencies}

                请优化后的核心竞争力（保持原有格式，直接列出每项能力）："""
        logging.info(f"Prompting LLM with: {prompt}")
        optimized_core_competencies = _siliconflow_call(prompt)
        logging.info(f"Optimized core competencies: {optimized_core_competencies}")
    except HTTPException as e:
        logging.error(f"LLM call failed: {e}")
        raise e

    # 更新简历中的CORE COMPETENCIES部分
    new_resume = old_resume_text.replace(core_competencies, optimized_core_competencies)
    logging.info("Replaced core competencies in resume text")

    # 生成新的简历PDF
    resume_pdf = generate_pdf(new_resume)
    logging.info("Generated new resume PDF")

    # 返回PDF文件
    logging.info("Sending PDF file")
    return StreamingResponse(BytesIO(resume_pdf.read()), media_type='application/pdf', headers={"Content-Disposition": "attachment;filename=optimized_resume.pdf"})
