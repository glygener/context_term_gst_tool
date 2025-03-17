

# Use an official Python runtime as a parent image
FROM python:3.8-buster

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including apt-utils and git
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    apt-utils \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install virtualenv globally
RUN pip install --upgrade pip && pip install virtualenv

# Create a virtual environment
RUN virtualenv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Clone the OGER repository before installing
RUN git clone https://github.com/OntoGene/OGER.git /app/OGER

# Install OGER from the cloned repository
RUN /app/venv/bin/pip install git+https://github.com/OntoGene/OGER.git

# Copy the entire project into the container
COPY . /app

# Ensure the necessary directories exist
RUN mkdir -p /app/Dictionary /app/OGER/oger/test/testfiles /app/mesh_to_doid /app/abstract_version \
/app/abstract_version/Outputs_Abstract /app/abstract_version/abstract_xml /app/abstract_version/abstract_text \
/app/abstract_version/Scripts_Abstract /app/full_length_version /app/full_length_version/bioc_xml_fl \
/app/full_length_version/output_text_section_FL /app/full_length_version/output_xml_section_FL \
/app/full_length_version/Outputs_FL /app/full_length_version/Scripts_FL \
/app/gst_abstract /app/gst_abstract/abstract_xml /app/gst_abstract/abstract_text \
/app/gst_abstract/Scripts /app/gst_abstract/Outputs /app/gst_abstract/Saved_Model \
/app/gst_full /app/gst_full/bioc_xml_fl /app/gst_full/output_xml_section_FL /app/gst_full/output_text_section_FL \
/app/gst_full/Scripts /app/gst_full/Outputs /app/gst_full/Saved_Model /app/Saved_Model


COPY saved_model.tar.gz /app/Saved_Model/

RUN tar -xzvf /app/Saved_Model/saved_model.tar.gz -C /app/gst_abstract/Saved_Model/ && \
    tar -xzvf /app/Saved_Model/saved_model.tar.gz -C /app/gst_full/Saved_Model/ && \
    rm /app/Saved_Model/saved_model.tar.gz  # Remove the tar file after extraction

# Install the dependencies for the rest of the project inside the virtual environment
RUN /app/venv/bin/pip install -r requirements.txt

RUN /app/venv/bin/python -m nltk.downloader punkt

# Copy the bash script to the container
COPY run_container.sh /app/run_container.sh

# Make the bash script executable
RUN chmod +x /app/run_container.sh

# Set the entry point to the bash script
ENTRYPOINT ["/app/run_container.sh"]