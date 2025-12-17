import requests
import time
import re
import logging

response_data={}
message="How are you"

try:
    ask_response = requests.post(
        "http://127.0.0.1:8100/ask",
        json={"question": message},
        timeout=10
    )
    ask_response.raise_for_status()
    response_data["text_output"] = ask_response.json().get("answer", "No answer")
    # response_data["text_output"] = ask_response.json()
except Exception as e:
    response_data["text_output"] = f"Error contacting /ask endpoint: {e}"

    
print(response_data)


# 初始化日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 模拟流式 chunk 生成器（每5个词一个chunk）
def generate_chunks(text, words_per_chunk=5):
    words = text.split()
    for i in range(0, len(words), words_per_chunk):
        yield " ".join(words[i:i + words_per_chunk])

# 主处理函数
def process_text(text):
    result = ""
    first = True
    start = time.perf_counter()

    for chunk in generate_chunks(text):
        if first:
            logger.info(f"llm Time to first chunk: {time.perf_counter() - start:.4f}s")
            first = False

        msg = chunk
        lastpos = 0
        for i, char in enumerate(msg):
            if char in ",.!;:，。！？：；":
                result += msg[lastpos:i + 1]
                lastpos = i + 1
                if len(result) > 10:
                    logger.info(result)
                    print("PUSH:", result)
                    result = ""
        result += msg[lastpos:]

    logger.info(f"llm Time to last chunk: {time.perf_counter() - start:.4f}s")
    if result:
        print("PUSH:", result)

# 示例输入
text = response_data["text_output"]

# 执行
process_text(text)
    