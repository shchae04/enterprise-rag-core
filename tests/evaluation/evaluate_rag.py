import asyncio
import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
# For Gemini support in Ragas, we might need custom LLM/Embeddings config
# But for simplicity, we assume OPENAI_API_KEY is present or we configure Ragas to use Gemini via LangChain wrapper
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.services.chat_service import ChatService
from app.core.database import AsyncSessionLocal
from app.core.config import settings

# Test Data (Golden Dataset)
TEST_QUESTIONS = [
    {
        "question": "RAG 시스템의 주요 특징은 무엇인가요?",
        "ground_truth": "RAG 시스템은 쿼리 확장, 하이브리드 검색, 재순위화 파이프라인을 통해 높은 정확도를 제공하며, 다양한 문서 포맷을 지원하고 엔터프라이즈급 아키텍처를 갖추고 있습니다."
    },
    {
        "question": "지원하는 문서 포맷에는 어떤 것들이 있나요?",
        "ground_truth": "HWP, PDF, DOCX, XLSX, TXT, MD 등 주요 문서 포맷을 지원합니다."
    },
    {
        "question": "백엔드 기술 스택은 무엇인가요?",
        "ground_truth": "백엔드는 FastAPI, PostgreSQL(pgvector), SQLAlchemy Async, Celery, Redis 등을 사용합니다."
    }
]

async def generate_rag_responses():
    """
    Generate answers using our actual RAG pipeline
    """
    results = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    print("🚀 Generating responses from RAG pipeline...")
    
    async with AsyncSessionLocal() as db:
        chat_service = ChatService(db)
        
        for item in TEST_QUESTIONS:
            query = item["question"]
            ground_truth = item["ground_truth"]
            
            # Call actual RAG
            answer, sources = await chat_service.get_answer(query)
            
            # Extract contexts
            context_texts = [s["content"] for s in sources]
            
            results["question"].append(query)
            results["answer"].append(answer)
            results["contexts"].append(context_texts)
            results["ground_truth"].append(ground_truth)
            
    return results

def run_evaluation():
    # 1. Generate Responses
    data_dict = asyncio.run(generate_rag_responses())
    dataset = Dataset.from_dict(data_dict)

    # 2. Configure Ragas with Gemini (if available) or OpenAI
    # If OPENAI_API_KEY is not set, this might fail unless we configure Gemini
    # Here we assume OpenAI key is available for evaluation (standard practice)
    # or we can wrap Gemini.
    
    print("📊 Running Ragas evaluation...")
    
    # Define metrics
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
    ]

    # Run evaluation
    results = evaluate(
        dataset=dataset,
        metrics=metrics,
    )

    # 3. Print Results
    print("\n================ RAG EVALUATION REPORT ================")
    print(results)
    df = results.to_pandas()
    print("\nDetailed Results:")
    print(df[['question', 'answer', 'faithfulness', 'answer_relevancy']])
    
    # Save report
    os.makedirs("tests/reports", exist_ok=True)
    df.to_csv("tests/reports/ragas_report.csv", index=False)
    print(f"\n✅ Report saved to tests/reports/ragas_report.csv")

if __name__ == "__main__":
    run_evaluation()
