#!/bin/bash

# Remove any existing container with the same name
docker rm -f context_term_init

echo "What do you want to process? (Enter 'abstract', 'full-length', or 'both' or 'gst_abstract' or 'gst_full')"
read choice

if [ "$choice" != "abstract" ] && [ "$choice" != "full-length" ] && [ "$choice" != "both" ] && [ "$choice" != "gst_full" ] && [ "$choice" != "gst_abstract" ]; then
    echo "Invalid choice. Please enter 'abstract', 'full-length', or 'both'. Exiting."
    exit 1
fi

IMAGE_NAME="shovan5795/context-term-tool-abs-full:latest"

echo "Would you like to use a new pmid.txt file? (yes/no)"
read use_new_pmid
PMID_MOUNT=""
if [ "$use_new_pmid" == "yes" ]; then
    echo "Please enter the full path to the new pmid.txt file:"
    read custom_pmid_path

    # Check if the provided file exists
    if [ -f "$custom_pmid_path" ]; then
        echo "Using the provided pmid.txt file: $custom_pmid_path"
        PMID_MOUNT="-v $custom_pmid_path:/app/test.txt"
    else
        echo "The provided file does not exist. Exiting."
        exit 1
    fi
else
    echo "Using the default pmid.txt file inside the container."
fi

if [ "$choice" == "abstract" ]; then
    BASE_DIR=$(pwd)/context_term_tool_abstract
    # Step 1: Create a folder for later use
    mkdir -p $BASE_DIR/Outputs_Abstract
    mkdir -p $BASE_DIR/abstract_xml
    mkdir -p $BASE_DIR/abstract_text

    docker volume create --driver local --opt type=none --opt device="$BASE_DIR" --opt o=bind

    # Step 3: Pull the Docker image from Docker Hub
    docker pull $IMAGE_NAME

    # Define a variable to hold the Docker run command
    ABSTRACT_DOCKER_CMD="docker run -it --name=context_term_init \
            -e MODE=$choice \
            -v $BASE_DIR/Outputs_Abstract:/app/abstract_version/Outputs_Abstract \
            -v $BASE_DIR/abstract_xml:/app/abstract_version/abstract_xml \
            -v $BASE_DIR/abstract_text:/app/abstract_version/abstract_text \
            $PMID_MOUNT $IMAGE_NAME"

    # Complete the Docker command with the image name
    ABSTRACT_DOCKER_CMD="$ABSTRACT_DOCKER_CMD $IMAGE_NAME"

    # Step 5: Run the Docker container with or without custom pmid.txt
    eval $ABSTRACT_DOCKER_CMD || { echo "Docker container failed to start."; exit 1; }

    # Step 6: Copy other important directories and files from the container to your local machine
    echo "Copying remaining files from the container to the local machine..."

    docker cp context_term_init:/app/Dictionary $BASE_DIR/Dictionary || { echo "Error copying Dictionary"; exit 1; }
    docker cp context_term_init:/app/OGER $BASE_DIR/OGER || { echo "Error copying OGER"; exit 1; }
    docker cp context_term_init:/app/mesh_to_doid $BASE_DIR/mesh_to_doid || { echo "Error copying mesh_to_doid"; exit 1; }
    docker cp context_term_init:/app/abstract_version/Scripts_Abstract $BASE_DIR/Scripts_Abstract || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/obo_to_tsv_tissue.py $BASE_DIR/obo_to_tsv_tissue.py || { echo "Error copying the script"; exit 1; }
    docker cp context_term_init:/app/requirements.txt $BASE_DIR/requirements.txt || { echo "Error copying the requirement file"; exit 1; }

    echo "Abstract version processing complete."


elif [ "$choice" == "full-length" ]; then
    BASE_DIR=$(pwd)/context_term_tool_full_length

    # Step 1: Create a folder for later use
    mkdir -p $BASE_DIR/Outputs_FL
    mkdir -p $BASE_DIR/bioc_xml_fl
    mkdir -p $BASE_DIR/output_text_section_FL
    mkdir -p $BASE_DIR/output_xml_section_FL

    docker volume create --driver local --opt type=none --opt device="$BASE_DIR" --opt o=bind

    # Step 3: Pull the Docker image from Docker Hub
    docker pull $IMAGE_NAME

    # Define a variable to hold the Docker run command
    FULL_LENGTH_DOCKER_CMD="docker run -it --name=context_term_init \
            -e MODE=$choice \
            -v $BASE_DIR/Outputs_FL:/app/full_length_version/Outputs_FL \
            -v $BASE_DIR/bioc_xml_fl:/app/full_length_version/bioc_xml_fl \
            -v $BASE_DIR/output_text_section_FL:/app/full_length_version/output_text_section_FL \
            -v $BASE_DIR/output_xml_section_FL:/app/full_length_version/output_xml_section_FL \
            $PMID_MOUNT $IMAGE_NAME"

    # Complete the Docker command with the image name
    FULL_LENGTH_DOCKER_CMD="$FULL_LENGTH_DOCKER_CMD $IMAGE_NAME"

    # Step 5: Run the Docker container with or without custom pmid.txt
    eval $FULL_LENGTH_DOCKER_CMD || { echo "Docker container failed to start."; exit 1; }

    # Step 6: Copy other important directories and files from the container to your local machine
    echo "Copying remaining files from the container to the local machine..."

    docker cp context_term_init:/app/Dictionary $BASE_DIR/Dictionary || { echo "Error copying Dictionary"; exit 1; }
    docker cp context_term_init:/app/OGER $BASE_DIR/OGER || { echo "Error copying OGER"; exit 1; }
    docker cp context_term_init:/app/mesh_to_doid $BASE_DIR/mesh_to_doid || { echo "Error copying mesh_to_doid"; exit 1; }
    docker cp context_term_init:/app/full_length_version/Scripts_FL $BASE_DIR/Scripts_FL || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/obo_to_tsv_tissue.py $BASE_DIR/obo_to_tsv_tissue.py || { echo "Error copying the script"; exit 1; }
    docker cp context_term_init:/app/requirements.txt $BASE_DIR/requirements.txt || { echo "Error copying the requirement file"; exit 1; }

    echo "Full-length version processing complete."


elif [ "$choice" == "both" ]; then
    BASE_DIR=$(pwd)/context_term_tool_abs_full

    # Step 1: Create a folder for later use
    mkdir -p $BASE_DIR/Outputs_Abstract
    mkdir -p $BASE_DIR/abstract_xml
    mkdir -p $BASE_DIR/abstract_text
    mkdir -p $BASE_DIR/Outputs_FL
    mkdir -p $BASE_DIR/bioc_xml_fl
    mkdir -p $BASE_DIR/output_text_section_FL
    mkdir -p $BASE_DIR/output_xml_section_FL

    docker volume create --driver local --opt type=none --opt device="$BASE_DIR" --opt o=bind

    # Step 3: Pull the Docker image from Docker Hub
    docker pull $IMAGE_NAME

    # Define a variable to hold the Docker run command
    DOCKER_CMD="docker run -it --name=context_term_init \
            -e MODE=$choice \
            -v $BASE_DIR/Outputs_Abstract:/app/abstract_version/Outputs_Abstract \
            -v $BASE_DIR/abstract_xml:/app/abstract_version/abstract_xml \
            -v $BASE_DIR/abstract_text:/app/abstract_version/abstract_text \
            -v $BASE_DIR/Outputs_FL:/app/full_length_version/Outputs_FL \
            -v $BASE_DIR/bioc_xml_fl:/app/full_length_version/bioc_xml_fl \
            -v $BASE_DIR/output_text_section_FL:/app/full_length_version/output_text_section_FL \
            -v $BASE_DIR/output_xml_section_FL:/app/full_length_version/output_xml_section_FL \
            $PMID_MOUNT $IMAGE_NAME"
    

    # Complete the Docker command with the image name
    DOCKER_CMD="$DOCKER_CMD $IMAGE_NAME"

    # Step 5: Run the Docker container with or without custom pmid.txt
    eval $DOCKER_CMD || { echo "Docker container failed to start."; exit 1; }

    # Step 6: Copy other important directories and files from the container to your local machine
    echo "Copying remaining files from the container to the local machine..."

    docker cp context_term_init:/app/Dictionary $BASE_DIR/Dictionary || { echo "Error copying Dictionary"; exit 1; }
    docker cp context_term_init:/app/OGER $BASE_DIR/OGER || { echo "Error copying OGER"; exit 1; }
    docker cp context_term_init:/app/mesh_to_doid $BASE_DIR/mesh_to_doid || { echo "Error copying mesh_to_doid"; exit 1; }
    docker cp context_term_init:/app/abstract_version/Scripts_Abstract $BASE_DIR/Scripts_Abstract || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/full_length_version/Scripts_FL $BASE_DIR/Scripts_FL || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/obo_to_tsv_tissue.py $BASE_DIR/obo_to_tsv_tissue.py || { echo "Error copying the script"; exit 1; }
    docker cp context_term_init:/app/requirements.txt $BASE_DIR/requirements.txt || { echo "Error copying the requirement file"; exit 1; }

    echo "Both Abstract and Full-length version processing complete."

elif [ "$choice" == "gst_abstract" ]; then
    BASE_DIR=$(pwd)/context_term_tool_gst_abstract
    # Step 1: Create a folder for later use
    mkdir -p $BASE_DIR/Outputs
    mkdir -p $BASE_DIR/abstract_xml
    mkdir -p $BASE_DIR/abstract_text

    docker volume create --driver local --opt type=none --opt device="$BASE_DIR" --opt o=bind

    # Step 3: Pull the Docker image from Docker Hub
    docker pull $IMAGE_NAME

    # Define a variable to hold the Docker run command
    ABSTRACT_DOCKER_CMD="docker run -it --name=context_term_init \
            -e MODE=$choice \
            -v $BASE_DIR/Outputs:/app/gst_abstract/Outputs \
            -v $BASE_DIR/abstract_xml:/app/gst_abstract/abstract_xml \
            -v $BASE_DIR/abstract_text:/app/gst_abstract/abstract_text \
            $PMID_MOUNT $IMAGE_NAME"

    # Complete the Docker command with the image name
    ABSTRACT_DOCKER_CMD="$ABSTRACT_DOCKER_CMD $IMAGE_NAME"

    # Step 5: Run the Docker container with or without custom pmid.txt
    eval $ABSTRACT_DOCKER_CMD || { echo "Docker container failed to start."; exit 1; }

    # Step 6: Copy other important directories and files from the container to your local machine
    echo "Copying remaining files from the container to the local machine..."

    docker cp context_term_init:/app/gst_abstract/Scripts $BASE_DIR/Scripts || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/gst_abstract/Saved_Model $BASE_DIR/Saved_Model || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/requirements.txt $BASE_DIR/requirements.txt || { echo "Error copying the requirement file"; exit 1; }

    echo "Abstract version processing complete."

elif [ "$choice" == "gst_full" ]; then
    BASE_DIR=$(pwd)/context_term_tool_gst_full_length
    # Step 1: Create a folder for later use
    mkdir -p $BASE_DIR/Outputs
    mkdir -p $BASE_DIR/bioc_xml_fl
    mkdir -p $BASE_DIR/output_xml_section_FL
    mkdir -p $BASE_DIR/output_text_section_FL

    docker volume create --driver local --opt type=none --opt device="$BASE_DIR" --opt o=bind

    # Step 3: Pull the Docker image from Docker Hub
    docker pull $IMAGE_NAME

    # Define a variable to hold the Docker run command
    ABSTRACT_DOCKER_CMD="docker run -it --name=context_term_init \
            -e MODE=$choice \
            -v $BASE_DIR/Outputs:/app/gst_full/Outputs \
            -v $BASE_DIR/bioc_xml_fl:/app/gst_full/bioc_xml_fl \
            -v $BASE_DIR/output_xml_section_FL:/app/gst_full/output_xml_section_FL \
            -v $BASE_DIR/output_text_section_FL:/app/gst_full/output_text_section_FL \
            $PMID_MOUNT $IMAGE_NAME"

    # Complete the Docker command with the image name
    ABSTRACT_DOCKER_CMD="$ABSTRACT_DOCKER_CMD $IMAGE_NAME"

    # Step 5: Run the Docker container with or without custom pmid.txt
    eval $ABSTRACT_DOCKER_CMD || { echo "Docker container failed to start."; exit 1; }

    # Step 6: Copy other important directories and files from the container to your local machine
    echo "Copying remaining files from the container to the local machine..."

    docker cp context_term_init:/app/gst_full/Scripts $BASE_DIR/Scripts || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/gst_full/Saved_Model $BASE_DIR/Saved_Model || { echo "Error copying Scripts"; exit 1; }
    docker cp context_term_init:/app/requirements.txt $BASE_DIR/requirements.txt || { echo "Error copying the requirement file"; exit 1; }

    echo "Full-length version processing complete."
    

fi

echo "All files and directories have been copied to the local machine."
