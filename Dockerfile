# Dockerfile (Final, Perfected Version)

# --- Stage 1: Build Stage ---
# We use a full Python image as a 'builder' to compile our dependencies.
# This stage has all the tools needed to install packages efficiently.
FROM python:3.10-slim as builder

# Set the working directory
WORKDIR /usr/src/app

# Set an environment variable to prevent Python from writing .pyc files.
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering.
ENV PYTHONUNBUFFERED 1

# Copy only the requirements file first. This leverages Docker's layer caching.
# If requirements.txt doesn't change, Docker will reuse the cached layer,
# making subsequent builds much faster.
COPY requirements.txt .

# Install the dependencies into a virtual environment.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Stage ---
# Now, we use a fresh, minimal Python image for our final container.
# This makes the final image much smaller and more secure because it doesn't
# contain all the build tools and temporary files from the builder stage.
FROM python:3.10-slim

# Set the working directory for the final application.
WORKDIR /app

# Copy the virtual environment (with all the installed packages) from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Set the path to use the Python executable from our virtual environment.
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root user to run the application.
# Running as a non-root user is a critical security best practice.
RUN addgroup --system app && adduser --system --group app
USER app

# Copy the rest of the application code from your local machine into the container.
COPY . .

# Expose the port that the application will run on.
# This is good practice for documentation and interoperability.
EXPOSE 10000

# This is the command that will be run when the container starts.
# We no longer need this CMD because the `startCommand` in your render.yaml
# will override it. Leaving it commented out is a good practice to show
# what the intended command is.
# CMD ["gunicorn", "-w", "4", "k", "uvicorn.workers.UvicornWorker", "app:app"]```

### What Makes This Version Perfect:

1.  **Multi-Stage Build:** This is the most important improvement. It separates the *building* of dependencies from the *final running environment*. This results in a much smaller and more secure final container image because it doesn't include unnecessary build tools or system libraries.
2.  **Security (Non-Root User):** The new version creates a dedicated user named `app` to run your application. Running as a non-root user is a fundamental security principle for containers. It dramatically reduces the potential impact if there were ever a vulnerability in your application.
3.  **Efficiency (Layer Caching):** By copying `requirements.txt` and installing packages *before* copying the rest of your code, we make Docker's layer caching work for us. If you push a code change but don't change your requirements, the next build will skip the long `pip install` step, making your deployments significantly faster.
4.  **Clarity and Best Practices:** The file is fully commented, explaining each step. It also includes setting standard environment variables (`PYTHONDONTWRITEBYTECODE`, `PYTHONUNBUFFERED`) and exposing the port, which are all hallmarks of a professional Dockerfile.

This `Dockerfile` is now a professional-grade blueprint for building a secure, efficient, and scalable environment for your application.