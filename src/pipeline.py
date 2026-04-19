from src.data_simulation import generate_retail_data
from src.data_preprocessing import preprocess_data
from src.eda import generate_eda_outputs
from src.forecasting import train_and_evaluate_model, generate_inventory_ready_dataset
from src.inventory import build_full_inventory_recommendations
from src.utils import ensure_directories

def run_full_pipeline():
    ensure_directories()

    print("Step 1: Generating synthetic retail dataset...")
    df = generate_retail_data()
    df.to_csv("data/retail_sales_data.csv", index=False)

    print("Step 2: Preprocessing dataset...")
    processed_df = preprocess_data("data/retail_sales_data.csv")
    processed_df.to_csv("outputs/final_sales_data.csv", index=False)

    print("Step 3: Generating EDA outputs...")
    generate_eda_outputs(processed_df)

    print("Step 4: Training forecasting model...")
    metrics_df, enriched_df = train_and_evaluate_model(processed_df)
    metrics_df.to_csv("outputs/model_metrics.csv", index=False)
    enriched_df.to_csv("outputs/model_ready_dataset.csv", index=False)

    print("Step 5: Building inventory recommendations...")
    inventory_df = build_full_inventory_recommendations(processed_df)
    inventory_df.to_csv("outputs/inventory_recommendations.csv", index=False)

    print("Pipeline completed successfully.")
    print("Files saved in data/, outputs/, and images/")