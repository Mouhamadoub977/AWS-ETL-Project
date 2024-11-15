import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col



## Cette classe gère la logique métier pour les transactions
""" Méthode qu'on a utiliser : calculate_total_amount(): Calculer le montant total de chaque transaction (Quantity * 
UnitPrice) et ajouter une colonne TotalAmount.
o group_by_country(): On va regrouper les données par pays et calculer la somme totale des 
montants des transactions pour chaque pays.
o aggregate_monthly_data(): Calcul des statistiques mensuelles, comme le montant 
total des ventes et le nombre de transactions """  


args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Début Classe 2 TransactionProcessor
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

# Chargerment des données nettoyées depuis l'emplacement intermédiaire
data = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    format="parquet",
    connection_options={"paths": ["s3://momo-projet-backet/data-intermediate/cleaned_data/"]},
    transformation_ctx="data"
)

df = data.toDF()
processor = TransactionProcessor(df)
processed_df = processor.calculate_total_amount().group_by_country()

# Stockage de l'agrégation par pays dans S3
country_dynamic_frame = DynamicFrame.fromDF(processed_df, glueContext, "country_dynamic_frame")
dat2 = "s3://momo-projet-backet/data-output/country_sales/"
glueContext.write_dynamic_frame.from_options(
    frame=country_dynamic_frame,
    connection_type="s3",
    connection_options={"path": dat2},
    format="parquet"
)

job.commit()


