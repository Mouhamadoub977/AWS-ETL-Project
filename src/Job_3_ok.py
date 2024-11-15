import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, month, year



""" Cette classe principale orchestre le processus ETL en appelant les méthodes des autres 
classes. Elle inclura également l’enregistrement final en parquet.
 Résumé Méthode :
o run_pipeline(): Exécute le pipeline ETL complet, nettoie les données, applique les 
transformations, et enregistre le DataFrame final.
o save_as_parquet(path: String): Enregistre le DataFrame final sous forme de fichier 
parquet."""


args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Classe DataCleaner pour le nettoyage
class DataCleaner:
    def __init__(self, df):
        self.df = df

    def remove_duplicates(self):
        self.df = self.df.dropDuplicates()
        return self

    def handle_missing_values(self):
        self.df = self.df.na.drop(subset=["CustomerID", "Description", "Quantity", "UnitPrice"])
        return self

    def filter_valid_transactions(self):
        self.df = self.df.filter(~self.df["InvoiceNo"].startswith("C"))
        return self

# Classe TransactionProcessor pour la transformation des données
class TransactionProcessor:
    def __init__(self, df):
        self.df = df

    def calculate_total_amount(self):
        self.df = self.df.withColumn("TotalAmount", col("Quantity") * col("UnitPrice"))
        return self

    def group_by_country(self):
        self.df = self.df.groupBy("Country").agg({"TotalAmount": "sum", "InvoiceNo": "count"}) \
                         .withColumnRenamed("sum(TotalAmount)", "TotalSales") \
                         .withColumnRenamed("count(InvoiceNo)", "TransactionCount")
        return self.df

    def aggregate_monthly_data(self):
        self.df = self.df.withColumn("Year", year(col("InvoiceDate"))).withColumn("Month", month(col("InvoiceDate")))
        self.df = self.df.groupBy("Year", "Month").agg({"TotalAmount": "sum", "InvoiceNo": "count"}) \
                         .withColumnRenamed("sum(TotalAmount)", "MonthlySales") \
                         .withColumnRenamed("count(InvoiceNo)", "MonthlyTransactionCount")
        return self.df

# Classe ETLPipeline pour orchestrer le pipeline ETL
class ETLPipeline:
    def __init__(self, df):
        self.df = df

    def run_pipeline(self):
        # Étape de nettoyage
        cleaner = DataCleaner(self.df)
        cleaned_df = cleaner.remove_duplicates().handle_missing_values().filter_valid_transactions().df

        # Étape de transformation
        processor = TransactionProcessor(cleaned_df)
        transformed_df = processor.calculate_total_amount().df

        # Agrégation mensuelle
        final_df = processor.aggregate_monthly_data()
        return final_df

    def save_as_parquet(self, df, path):
        # Conversion en DynamicFrame pour l’écriture
        dynamic_frame = DynamicFrame.fromDF(df, glueContext, "final_dynamic_frame")
        glueContext.write_dynamic_frame.from_options(
            frame=dynamic_frame,
            connection_type="s3",
            connection_options={"path": path},
            format="parquet"
        )

# Chargement des données depuis S3
data = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False},
    connection_type="s3",
    format="csv",
    connection_options={"paths": ["s3://momo-projet-backet/data-input-mohamdou/Retail.csv"], "recurse": True},
    transformation_ctx="data"
)

# Conversion en df Spark
df = data.toDF()

# Run du pipeline ETL
pipeline = ETLPipeline(df)
final_df = pipeline.run_pipeline()

# Stock du résult final en Parquet
dat_3_ok = "s3://momo-projet-backet/data-output/final_output/"
pipeline.save_as_parquet(final_df, dat_3_ok)

job.commit()



