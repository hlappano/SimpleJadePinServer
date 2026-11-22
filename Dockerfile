# Use official Python runtime as parent image
FROM python:3.13.2-bullseye

#
# Environment Variables
#
ENV NODE_JS_VERSION=26.8.2
ENV NODE_LINUX=node-v${NODE_JS_VERSION}-linux
ENV NODE_JS_DL_PATH=https://nodejs.org/download/release/v${NODE_JS_VERSION}/${NODE_LINUX}

#
# Python Setup
#
# Copy the requirements file
COPY requirements.txt .
# Install Python dependencies
RUN pip install --upgrade pip && pip install -U --no-cache-dir --require-hashes -r requirements.txt

# Create user permissions
RUN useradd -m -u 1000 app

# Set the working directory
WORKDIR /app

#
# Install Node JS
#
RUN u_arch=$(uname -m) && \
    case "${u_arch}" in \
        x86_64) arch="x64" ;; \
        armv7l) arch="armv7l" ;; \
        aarch64) arch="arm64" ;; \
        *) echo "Unsupported architecture: ${arch}" && exit 1 ;; \
    esac && \
    curl -SL "${NODE_JS_DL_PATH}-${arch}.tar.gz" | tar -xzC /app && \
    mv /app/${NODE_LINUX}-${arch} /app/${NODE_LINUX}

# Set the PATH to include Node.js
ENV PATH="${PATH}:/app/${NODE_LINUX}/bin"

#
# Copy the application code
#
COPY ./server /app/server
COPY ./web /app/web
COPY ./startup.sh /app/startup.sh

#
# Install dependencies for frontend
#
RUN cd /app/web && \
    # Install Node.js dependencies
    npm install && \
    # Build
    npm run build && \
    # Go back to the app directory
    cd /app

# Set the permissions
RUN chown -R app:app .

# Expose the port
EXPOSE 5000 4443

# Setup entrypoint
ENTRYPOINT [ "/app/startup.sh" ]

# Start Application as Root
USER root