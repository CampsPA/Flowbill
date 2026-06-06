# DockerFile

# Setup image
FROM python:3.12.12-slim


# Create working directory
WORKDIR /app


# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Pass the full path for alembic
ENV PATH="/usr/local/bin:$PATH" 


# Install the application dependencies
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


# Create a non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Create logs directory with correct ownership
RUN mkdir -p /app/logs && chown appuser:appgroup /app/logs


# Copy source code
COPY --chown=appuser:appgroup app/ ./app/ 
COPY --chown=appuser:appgroup alembic.ini .
COPY --chown=appuser:appgroup alembic/ ./alembic/
# Copy the entrypoint script into the image
COPY --chown=appuser:appgroup entrypoint.sh . 
# Make it executable 
RUN chmod +x entrypoint.sh


# Switch to non-root user
USER appuser

# Expose - Documenting the port
EXPOSE 8000

# Reference the entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# CMD - Runtime Command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

