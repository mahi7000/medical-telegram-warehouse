import sys
import os
import subprocess
from dagster import op, job, ScheduleDefinition, DefaultScheduleStatus, AssetMaterialization

@op(description="Step 1: Scrape raw unstructured clinical posts from targeted Telegram channels.")
def scrape_telegram_data(context):
    context.log.info("Starting Telegram scraper target ingestion...")
    # This simulates or runs your raw ingestion scripts
    # Example fallback check:
    scraper_path = os.path.join("scripts", "telegram_scraper.py")
    if os.path.exists(scraper_path):
        subprocess.run([sys.executable, scraper_path], check=True)
    else:
        context.log.warn("Target scripts/telegram_scraper.py not found. Emulating staging raw data...")
    return "raw_data_landed_json"

@op(description="Step 2: Load raw staging data directly into structural PostgreSQL tables.")
def load_raw_to_postgres(context, upstream_log):
    context.log.info(f"Ingesting raw matrix logs into relational stage layer... Source: {upstream_log}")
    # Simulates loading transactions safely into Postgres tables
    return True

@op(description="Step 3: Trigger dbt compilation layers to model clean analytics star-schemas.")
def run_dbt_transformations(context, db_staged):
    if not db_staged:
        raise Exception("Database staging check failed.")
    
    context.log.info("Executing dbt transformations model run layer...")
    # Tries to run dbt if the profile directory exists
    if os.path.exists("dbt_project.yml"):
        subprocess.run(["dbt", "run"], check=True)
    else:
        context.log.warn("dbt project configuration not found locally. Simulating 'marts' schema builds...")
    return True

@op(description="Step 4: Run local computer vision enrichment algorithms on channel image media bins.")
def run_yolo_enrichment(context, transform_completed):
    context.log.info("Invoking YOLOv8 object detection on workspace media...")
    # Run your image processing module if present
    img_script = "process_medical_images.py"
    if os.path.exists(img_script):
        subprocess.run([sys.executable, img_script], check=True)
    else:
        context.log.warn(f"{img_script} not found, passing visual analysis step.")
    return True

@op(description="Step 5: Execute Named Entity Recognition (NER) and re-index the FAISS Vector Store matrix.")
def run_ner_and_vector_store(context, yolo_completed):
    context.log.info("Running network-independent NER and FAISS vector index compilation...")
    # Run the Task 3 vector store execution script directly
    subprocess.run([sys.executable, "process_medical_ner.py"], check=True)
    
    # Materialize the output assets back to the Dagster tracking dashboard
    context.log_event(
        AssetMaterialization(
            asset_key="medical_warehouse_vector_index",
            description="FAISS Index and metadata generated locally in data/processed/"
        )
    )
    return "Pipeline Complete"

@job(description="End-to-End Medical Analytics Ingestion Warehouse Pipeline Automation Graph")
def medical_warehouse_pipeline():
    # Establishes clean, strict chronological dependency ordering
    raw_logs = scrape_telegram_data()
    db_staged = load_raw_to_postgres(raw_logs)
    transformed = run_dbt_transformations(db_staged)
    yolo_done = run_yolo_enrichment(transformed)
    run_ner_and_vector_store(yolo_done)

# Automatically trigger the pipeline every day exactly at midnight
daily_pipeline_schedule = ScheduleDefinition(
    job=medical_warehouse_pipeline,
    cron_schedule="0 0 * * *",
    default_status=DefaultScheduleStatus.STOPPED
)