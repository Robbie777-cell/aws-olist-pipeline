import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

RAW = "s3://data-pipeline-rob-2026/raw/olist"
PROCESSED = "s3://data-pipeline-rob-2026/processed"

def leer_csv(ruta):
    return spark.read \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .option("quote", '"') \
        .option("escape", '"') \
        .csv(ruta)

# orders
df = leer_csv(f"{RAW}/olist_orders/")
print(f"orders: {df.count()} filas")
df.write.mode("overwrite").parquet(f"{PROCESSED}/orders/")

# customers
df = leer_csv(f"{RAW}/olist_customers/")
print(f"customers: {df.count()} filas")
df.write.mode("overwrite").parquet(f"{PROCESSED}/customers/")

# order_items
df = leer_csv(f"{RAW}/olist_order_items/")
print(f"order_items: {df.count()} filas")
df.write.mode("overwrite").parquet(f"{PROCESSED}/order_items/")

# order_payments
df = leer_csv(f"{RAW}/olist_order_payments/")
print(f"order_payments: {df.count()} filas")
df.write.mode("overwrite").parquet(f"{PROCESSED}/order_payments/")

# products
df = leer_csv(f"{RAW}/olist_products/")
print(f"products: {df.count()} filas")
df.write.mode("overwrite").parquet(f"{PROCESSED}/products/")

print("ETL completado")
job.commit()