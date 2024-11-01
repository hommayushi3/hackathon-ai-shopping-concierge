import os

import pandas as pd
from realtime.product_search.base import ProductSearch


DATA_DIR = "data"
IMAGES_DIR = os.path.join(DATA_DIR, "product_catalog_images")
CSV_FILE = os.path.join(DATA_DIR, "product_catalog.csv")
BATCH_SIZE = 96

with open(CSV_FILE) as f:
    products_df = pd.read_csv(f).fillna("")
print("Product catalog loaded from csv.")

# Instantiate ProductSearch
product_search = ProductSearch()
print("ProductSearch instantiated.")

products_df["on_sale"] = products_df["on_sale"].apply({0: "Regular Price", 1: "On Sale"}.get)

# Load the product catalog
# product_search.add_products(
#     products_df=products_df,
#     images_dir=IMAGES_DIR,
#     batch_size=BATCH_SIZE
# )
print("Product catalog indexed.")

product_search.init_metadata_searchers()
print("Product metadata searchers initialized.")

# for metadata_searcher in product_search.metadata_searchers.values():
#     metadata_searcher.add_metadata(products_df, batch_size=BATCH_SIZE)
# print(product_search.metadata_searchers["on_sale"].index.describe_index_stats().get('total_vector_count', 0))
print("Product metadata search index populated.")
