import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame




""" Résumé méthode : remove_duplicates(): Pour supprimer les lignes en double du DataFrame.
o handle_missing_values(): Traitement des valeurs manquantes dans les colonnes critiques 
(CustomerID, Description, Quantity, etc.).
o filter_valid_transactions(): Garde uniquement les transactions non annulées. """


args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Classe 1 DataCleaner
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

# Chargeons les données depuis S3
data = glueContext.create_dynamic_frame.from_options(
    format_options={"quoteChar": "\"", "withHeader": True, "separator": ",", "optimizePerformance": False},
    connection_type="s3",
    format="csv",
    connection_options={"paths": ["s3://momo-projet-backet/data-input-mohamdou/Retail.csv"], "recurse": True},
    transformation_ctx="data"
)

df = data.toDF()
cleaner = DataCleaner(df)
cleaned_df = cleaner.remove_duplicates().handle_missing_values().filter_valid_transactions().df


cleaned_dynamic_frame = DynamicFrame.fromDF(cleaned_df, glueContext, "cleaned_dynamic_frame")
dat1 = "s3://momo-projet-backet/data-intermediate/cleaned_data/"
glueContext.write_dynamic_frame.from_options(
    frame=cleaned_dynamic_frame,
    connection_type="s3",
    connection_options={"path": dat1},
    format="parquet"
)

job.commit()


