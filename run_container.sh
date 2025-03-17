#!/bin/bash

# Activate the virtual environment
source /app/venv/bin/activate

MODE=${MODE:-gst_full}

echo "Running obo_to_tsv_tissue.py..."
python3 /app/obo_to_tsv_tissue.py
if [ $? -ne 0 ]; then
    echo "Error running obo_to_tsv_tissue.py"
    exit 1
fi
echo "Successfully completed running obo_to_tsv_tissue.py"

# Step 1: Convert OBO files to TSV (Tissue)

if [ "$MODE" == "abstract" ]; then
    echo "Abstract processing started"

    # Step 2: Running other scripts
    echo "Running pubtator_api.py..."
    python3 /app/abstract_version/Scripts_Abstract/1_pubtator_api.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_pubtator_api.py"
        exit 1
    fi
    echo "Successfully completed running 1_pubtator_api.py"

    echo "Running 2_dis_spec_cell_tis_prot.py..."
    python3 /app/abstract_version/Scripts_Abstract/2_dis_spec_cell_tis_prot.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_dis_spec_cell_tis_prot.py"
        exit 1
    fi
    echo "Successfully completed running 2_dis_spec_cell_tis_prot.py"

    echo "Running 3_get_sentence.py..."
    python3 /app/abstract_version/Scripts_Abstract/3_get_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_get_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 3_get_sentence.py"


    echo "Running 4_site_detector_tool.py..."
    python3 /app/abstract_version/Scripts_Abstract/4_site_detector_tool.py
    if [ $? -ne 0 ]; then
        echo "Error running 4_site_detector_tool.py"
        exit 1
    fi
    echo "Successfully completed running 4_site_detector_tool.py"


    echo "Running 5_site_filter.py..."
    python3 /app/abstract_version/Scripts_Abstract/5_site_filter.py
    if [ $? -ne 0 ]; then
        echo "Error running 5_site_filter.py"
        exit 1
    fi
    echo "Successfully completed running 5_site_filter.py"

    echo "Running 6_site_sent_fill.py..."
    python3 /app/abstract_version/Scripts_Abstract/6_site_sent_fill.py
    if [ $? -ne 0 ]; then
        echo "Error running 6_site_sent_fill.py"
        exit 1
    fi
    echo "Successfully completed running 6_site_sent_fill.py"


    echo "Running 7_sent_index_update.py..."
    python3 /app/abstract_version/Scripts_Abstract/7_sent_index_update.py
    if [ $? -ne 0 ]; then
        echo "Error running 7_sent_index_update.py"
        exit 1
    fi
    echo "Successfully completed running 7_sent_index_update.py"

    echo "Running 8_fill_site_info.py..."
    python3 /app/abstract_version/Scripts_Abstract/8_fill_site_info.py
    if [ $? -ne 0 ]; then
        echo "Error running 8_fill_site_info.py"
        exit 1
    fi
    echo "Successfully completed running 8_fill_site_info.py"


    echo "Running 9_final_excel.py..."
    python3 /app/abstract_version/Scripts_Abstract/9_final_excel.py
    if [ $? -ne 0 ]; then
        echo "Error running 9_final_excel.py"
        exit 1
    fi
    echo "Successfully completed running 9_final_excel.py"


    echo "Running 10_filter_entity.py..."
    python3 /app/abstract_version/Scripts_Abstract/10_filter_entity.py
    if [ $? -ne 0 ]; then
        echo "Error running 10_filter_entity.py"
        exit 1
    fi
    echo "Successfully completed running 10_filter_entity.py"


    echo "Running 11_html_creation.py..."
    python3 /app/abstract_version/Scripts_Abstract/11_html_creation.py
    if [ $? -ne 0 ]; then
        echo "Error running 11_html_creation.py"
        exit 1
    fi
    echo "Successfully completed running 11_html_creation.py"

elif [ "$MODE" == "full-length" ]; then
    echo "Full Length Tool Processing Started"

    echo "Running 1_pubtator_pmc_oa.py..."
    python3 /app/full_length_version/Scripts_FL/1_pubtator_pmc_oa.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_pubtator_pmc_oa.py"
        exit 1
    fi
    echo "Successfully completed running 1_pubtator_pmc_oa.py"

    echo "Running 2_oa_fl.py..."
    python3 /app/full_length_version/Scripts_FL/2_oa_fl.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_oa_fl.py"
        exit 1
    fi
    echo "Successfully completed running 2_oa_fl.py"

    echo "Running 3_fl_sections.py..."
    python3 /app/full_length_version/Scripts_FL/3_fl_sections.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_fl_sections.py"
        exit 1
    fi
    echo "Successfully completed running 3_fl_sections.py"

    echo "Running 4_fl_dis_spec_cel_tis_prot.py..."
    python3 /app/full_length_version/Scripts_FL/4_fl_dis_spec_cel_tis_prot.py
    if [ $? -ne 0 ]; then
        echo "Error running 4_fl_dis_spec_cel_tis_prot.py"
        exit 1
    fi
    echo "Successfully completed running 4_fl_dis_spec_cel_tis_prot.py"

    echo "Running 5_post_proc.py..."
    python3 /app/full_length_version/Scripts_FL/5_post_proc.py
    if [ $? -ne 0 ]; then
        echo "Error running 5_post_proc.py"
        exit 1
    fi
    echo "Successfully completed running 5_post_proc.py"

    echo "Running 6_get_sentence.py..."
    python3 /app/full_length_version/Scripts_FL/6_get_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 6_get_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 6_get_sentence.py"


    echo "Running 7_new_column_sentence.py..."
    python3 /app/full_length_version/Scripts_FL/7_new_column_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 7_new_column_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 7_new_column_sentence.py"


    echo "Running 8_sentence_match.py..."
    python3 /app/full_length_version/Scripts_FL/8_sentence_match.py
    if [ $? -ne 0 ]; then
        echo "Error running 8_sentence_match.py"
        exit 1
    fi
    echo "Successfully completed running 8_sentence_match.py"


    echo "Running 9_site_detector_tool.py..."
    python3 /app/full_length_version/Scripts_FL/9_site_detector_tool.py
    if [ $? -ne 0 ]; then
        echo "Error running 9_site_detector_tool.py"
        exit 1
    fi
    echo "Successfully completed running 9_site_detector_tool.py"


    echo "Running 10_site_filter.py..."
    python3 /app/full_length_version/Scripts_FL/10_site_filter.py
    if [ $? -ne 0 ]; then
        echo "Error running 10_site_filter.py"
        exit 1
    fi
    echo "Successfully completed running 10_site_filter.py"


    echo "Running 11_site_sent_fill.py..."
    python3 /app/full_length_version/Scripts_FL/11_site_sent_fill.py
    if [ $? -ne 0 ]; then
        echo "Error running 11_site_sent_fill.py"
        exit 1
    fi
    echo "Successfully completed running 11_site_sent_fill.py"


    echo "Running 12_fill_site_info.py..."
    python3 /app/full_length_version/Scripts_FL/12_fill_site_info.py
    if [ $? -ne 0 ]; then
        echo "Error running 12_fill_site_info.py"
        exit 1
    fi
    echo "Successfully completed running 12_fill_site_info.py"


    echo "Running 13_pmid_fill_for_site.py..."
    python3 /app/full_length_version/Scripts_FL/13_pmid_fill_for_site.py
    if [ $? -ne 0 ]; then
        echo "Error running 13_pmid_fill_for_site.py"
        exit 1
    fi
    echo "Successfully completed running 13_pmid_fill_for_site.py"


    echo "Running 14_final_excel.py..."
    python3 /app/full_length_version/Scripts_FL/14_final_excel.py
    if [ $? -ne 0 ]; then
        echo "Error running 14_final_excel.py"
        exit 1
    fi
    echo "Successfully completed running 14_final_excel.py"


    echo "Running 15_html_creation.py..."
    python3 /app/full_length_version/Scripts_FL/15_html_creation.py
    if [ $? -ne 0 ]; then
        echo "Error running 15_html_creation.py"
        exit 1
    fi
    echo "Successfully completed running 15_html_creation.py"


    echo "All scripts executed successfully!"


elif [ "$MODE" == "both" ]; then
    echo "Abstract processing started"

    # Step 2: Running other scripts
    echo "Running pubtator_api.py..."
    python3 /app/abstract_version/Scripts_Abstract/1_pubtator_api.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_pubtator_api.py"
        exit 1
    fi
    echo "Successfully completed running 1_pubtator_api.py"

    echo "Running 2_dis_spec_cell_tis_prot.py..."
    python3 /app/abstract_version/Scripts_Abstract/2_dis_spec_cell_tis_prot.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_dis_spec_cell_tis_prot.py"
        exit 1
    fi
    echo "Successfully completed running 2_dis_spec_cell_tis_prot.py"

    echo "Running 3_get_sentence.py..."
    python3 /app/abstract_version/Scripts_Abstract/3_get_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_get_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 3_get_sentence.py"


    echo "Running 4_site_detector_tool.py..."
    python3 /app/abstract_version/Scripts_Abstract/4_site_detector_tool.py
    if [ $? -ne 0 ]; then
        echo "Error running 4_site_detector_tool.py"
        exit 1
    fi
    echo "Successfully completed running 4_site_detector_tool.py"


    echo "Running 5_site_filter.py..."
    python3 /app/abstract_version/Scripts_Abstract/5_site_filter.py
    if [ $? -ne 0 ]; then
        echo "Error running 5_site_filter.py"
        exit 1
    fi
    echo "Successfully completed running 5_site_filter.py"

    echo "Running 6_site_sent_fill.py..."
    python3 /app/abstract_version/Scripts_Abstract/6_site_sent_fill.py
    if [ $? -ne 0 ]; then
        echo "Error running 6_site_sent_fill.py"
        exit 1
    fi
    echo "Successfully completed running 6_site_sent_fill.py"


    echo "Running 7_sent_index_update.py..."
    python3 /app/abstract_version/Scripts_Abstract/7_sent_index_update.py
    if [ $? -ne 0 ]; then
        echo "Error running 7_sent_index_update.py"
        exit 1
    fi
    echo "Successfully completed running 7_sent_index_update.py"

    echo "Running 8_fill_site_info.py..."
    python3 /app/abstract_version/Scripts_Abstract/8_fill_site_info.py
    if [ $? -ne 0 ]; then
        echo "Error running 8_fill_site_info.py"
        exit 1
    fi
    echo "Successfully completed running 8_fill_site_info.py"


    echo "Running 9_final_excel.py..."
    python3 /app/abstract_version/Scripts_Abstract/9_final_excel.py
    if [ $? -ne 0 ]; then
        echo "Error running 9_final_excel.py"
        exit 1
    fi
    echo "Successfully completed running 9_final_excel.py"


    echo "Running 10_filter_entity.py..."
    python3 /app/abstract_version/Scripts_Abstract/10_filter_entity.py
    if [ $? -ne 0 ]; then
        echo "Error running 10_filter_entity.py"
        exit 1
    fi
    echo "Successfully completed running 10_filter_entity.py"


    echo "Running 11_html_creation.py..."
    python3 /app/abstract_version/Scripts_Abstract/11_html_creation.py
    if [ $? -ne 0 ]; then
        echo "Error running 11_html_creation.py"
        exit 1
    fi
    echo "Successfully completed running 11_html_creation.py"

    echo "Full Length Tool Processing Started"

    echo "Running 1_pubtator_pmc_oa.py..."
    python3 /app/full_length_version/Scripts_FL/1_pubtator_pmc_oa.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_pubtator_pmc_oa.py"
        exit 1
    fi
    echo "Successfully completed running 1_pubtator_pmc_oa.py"

    echo "Running 2_oa_fl.py..."
    python3 /app/full_length_version/Scripts_FL/2_oa_fl.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_oa_fl.py"
        exit 1
    fi
    echo "Successfully completed running 2_oa_fl.py"

    echo "Running 3_fl_sections.py..."
    python3 /app/full_length_version/Scripts_FL/3_fl_sections.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_fl_sections.py"
        exit 1
    fi
    echo "Successfully completed running 3_fl_sections.py"

    echo "Running 4_fl_dis_spec_cel_tis_prot.py..."
    python3 /app/full_length_version/Scripts_FL/4_fl_dis_spec_cel_tis_prot.py
    if [ $? -ne 0 ]; then
        echo "Error running 4_fl_dis_spec_cel_tis_prot.py"
        exit 1
    fi
    echo "Successfully completed running 4_fl_dis_spec_cel_tis_prot.py"

    echo "Running 5_post_proc.py..."
    python3 /app/full_length_version/Scripts_FL/5_post_proc.py
    if [ $? -ne 0 ]; then
        echo "Error running 5_post_proc.py"
        exit 1
    fi
    echo "Successfully completed running 5_post_proc.py"

    echo "Running 6_get_sentence.py..."
    python3 /app/full_length_version/Scripts_FL/6_get_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 6_get_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 6_get_sentence.py"


    echo "Running 7_new_column_sentence.py..."
    python3 /app/full_length_version/Scripts_FL/7_new_column_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 7_new_column_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 7_new_column_sentence.py"


    echo "Running 8_sentence_match.py..."
    python3 /app/full_length_version/Scripts_FL/8_sentence_match.py
    if [ $? -ne 0 ]; then
        echo "Error running 8_sentence_match.py"
        exit 1
    fi
    echo "Successfully completed running 8_sentence_match.py"


    echo "Running 9_site_detector_tool.py..."
    python3 /app/full_length_version/Scripts_FL/9_site_detector_tool.py
    if [ $? -ne 0 ]; then
        echo "Error running 9_site_detector_tool.py"
        exit 1
    fi
    echo "Successfully completed running 9_site_detector_tool.py"


    echo "Running 10_site_filter.py..."
    python3 /app/full_length_version/Scripts_FL/10_site_filter.py
    if [ $? -ne 0 ]; then
        echo "Error running 10_site_filter.py"
        exit 1
    fi
    echo "Successfully completed running 10_site_filter.py"


    echo "Running 11_site_sent_fill.py..."
    python3 /app/full_length_version/Scripts_FL/11_site_sent_fill.py
    if [ $? -ne 0 ]; then
        echo "Error running 11_site_sent_fill.py"
        exit 1
    fi
    echo "Successfully completed running 11_site_sent_fill.py"


    echo "Running 12_fill_site_info.py..."
    python3 /app/full_length_version/Scripts_FL/12_fill_site_info.py
    if [ $? -ne 0 ]; then
        echo "Error running 12_fill_site_info.py"
        exit 1
    fi
    echo "Successfully completed running 12_fill_site_info.py"


    echo "Running 13_pmid_fill_for_site.py..."
    python3 /app/full_length_version/Scripts_FL/13_pmid_fill_for_site.py
    if [ $? -ne 0 ]; then
        echo "Error running 13_pmid_fill_for_site.py"
        exit 1
    fi
    echo "Successfully completed running 13_pmid_fill_for_site.py"


    echo "Running 14_final_excel.py..."
    python3 /app/full_length_version/Scripts_FL/14_final_excel.py
    if [ $? -ne 0 ]; then
        echo "Error running 14_final_excel.py"
        exit 1
    fi
    echo "Successfully completed running 14_final_excel.py"


    echo "Running 15_html_creation.py..."
    python3 /app/full_length_version/Scripts_FL/15_html_creation.py
    if [ $? -ne 0 ]; then
        echo "Error running 15_html_creation.py"
        exit 1
    fi
    echo "Successfully completed running 15_html_creation.py"


    echo "All scripts executed successfully!"

elif [ "$MODE" == "gst_abstract" ]; then
    echo "GST Abstract Tool Processing Started"

    echo "Running 1_pubtator_api.py..."
    python3 /app/gst_abstract/Scripts/1_pubtator_api.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_pubtator_api.py"
        exit 1
    fi
    echo "Successfully completed running 1_pubtator_api.py"

    echo "Running 2_text_file.py..."
    python3 /app/gst_abstract/Scripts/2_text_file.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_text_file.py"
        exit 1
    fi
    echo "Successfully completed running 2_text_file.py"

    echo "Running 3_get_sentence.py..."
    python3 /app/gst_abstract/Scripts/3_get_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_get_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 3_get_sentence.py"

    echo "Running 1_gst.py..."
    python3 /app/gst_abstract/Scripts/1_gst.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_gst.py"
        exit 1
    fi
    echo "Successfully completed running 1_gst.py"

    echo "Running 2_gst.py..."
    python3 /app/gst_abstract/Scripts/2_gst.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_gst.py"
        exit 1
    fi
    echo "Successfully completed running 2_gst.py"

    echo "Running 3_gst.py..."
    python3 /app/gst_abstract/Scripts/3_gst.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_gst.py"
        exit 1
    fi
    echo "Successfully completed running 3_gst.py"


    echo "Running 4_gst.py..."
    python3 /app/gst_abstract/Scripts/4_gst.py
    if [ $? -ne 0 ]; then
        echo "Error running 4_gst.py"
        exit 1
    fi
    echo "Successfully completed running 4_gst.py"

    echo "All scripts executed successfully!"

elif [ "$MODE" == "gst_full" ]; then
    echo "GST Full-length Tool Processing Started"

    echo "Running 1_pubtator_pmc_oa.py..."
    python3 /app/gst_full/Scripts/1_pubtator_pmc_oa.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_pubtator_pmc_oa.py"
        exit 1
    fi
    echo "Successfully completed running 1_pubtator_pmc_oa.py"

    echo "Running 2_oa_fl.py..."
    python3 /app/gst_full/Scripts/2_oa_fl.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_oa_fl.py"
        exit 1
    fi
    echo "Successfully completed running 2_oa_fl.py"

    echo "Running 3_fl_sections.py..."
    python3 /app/gst_full/Scripts/3_fl_sections.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_fl_sections.py"
        exit 1
    fi
    echo "Successfully completed running 3_fl_sections.py"

    echo "Running 6_get_sentence.py..."
    python3 /app/gst_full/Scripts/6_get_sentence.py
    if [ $? -ne 0 ]; then
        echo "Error running 6_get_sentence.py"
        exit 1
    fi
    echo "Successfully completed running 3_get_sentence.py"

    echo "Running 1_gst.py..."
    python3 /app/gst_full/Scripts/1_gst.py
    if [ $? -ne 0 ]; then
        echo "Error running 1_gst.py"
        exit 1
    fi
    echo "Successfully completed running 1_gst.py"

    echo "Running 2_gst.py..."
    python3 /app/gst_full/Scripts/2_gst.py
    if [ $? -ne 0 ]; then
        echo "Error running 2_gst.py"
        exit 1
    fi
    echo "Successfully completed running 2_gst.py"

    echo "Running 3_gst.py..."
    python3 /app/gst_full/Scripts/3_gst.py
    if [ $? -ne 0 ]; then
        echo "Error running 3_gst.py"
        exit 1
    fi
    echo "Successfully completed running 3_gst.py"


    echo "Running 4_gst_full.py..."
    python3 /app/gst_full/Scripts/4_gst_full.py
    if [ $? -ne 0 ]; then
        echo "Error running 4_gst_full.py"
        exit 1
    fi
    echo "Successfully completed running 4_gst_full.py"

    echo "All scripts executed successfully!"


else
    echo "Invalid mode specified: $MODE. Please use 'abstract', 'full-length', 'both' or 'gst'. Exiting."
    exit 1
fi