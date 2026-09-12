FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" python-multipart pillow bcrypt

COPY src/ ./src/
COPY frontend/ ./frontend/
COPY samples/ ./samples/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.inference_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
