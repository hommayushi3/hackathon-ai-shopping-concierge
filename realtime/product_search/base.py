# Create new index
import asyncio
import os
from functools import lru_cache
from typing import Dict, List, Optional

import chainlit as cl
import cohere
import pandas as pd
from pinecone import Pinecone, ServerlessSpec
from realtime.vision import image_to_data_uri
from tqdm import tqdm


AWS_REGION = "us-west-2"
MODEL_NAME = "embed-multilingual-light-v3.0"
PRODUCT_INDEX_NAME = "products"
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
COHERE_API_KEY = os.environ.get('COHERE_API_KEY')


class MetadataSearch:
    def __init__(self, column_name: str):
        """
        Initialize metadata search for a specific column.
        
        Args:
            column_name: Name of the column to search within
            PINECONE_API_KEY: Optional API key for Pinecone (defaults to environment variable)
            COHERE_API_KEY: Optional API key for Cohere (defaults to environment variable)
        """
        self.column_name = column_name
        self.pc = Pinecone(api_key=PINECONE_API_KEY or os.environ.get('PINECONE_API_KEY'))
        self.co = cohere.Client(COHERE_API_KEY or os.environ.get('COHERE_API_KEY'))
        self.embedding_dimension = 384  # Cohere embed-multilingual-light-v3.0 dimension
        self.index = None
        self.create_index()

    def create_index(self) -> None:
        """
        Create a new Pinecone index if it doesn't exist and connect to it.
        
        Args:
            index_name: Name of the Pinecone index to create/connect to
        """
        index_name = (self.column_name + "_index").replace("_", "-").lower()
        if index_name not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=index_name,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws',
                    region=AWS_REGION
                )
            )
        self.index = self.pc.Index(index_name)

    def _process_metadata_batch(self, batch_df: pd.DataFrame) -> List[tuple]:
        """
        Process a batch of metadata values and create vectors for upsert.
        
        Args:
            batch_df: DataFrame containing the batch of metadata values
            
        Returns:
            List of tuples containing (id, vector, metadata) for Pinecone upsert
        """
        to_upsert = []
        
        # Get unique values from the column
        unique_values = batch_df[self.column_name].dropna().unique()
        
        if len(unique_values) == 0:
            return to_upsert
            
        # Create descriptions for embedding
        descriptions = []
        valid_values = []
        
        for value in unique_values:
            # Create a description that includes both the value and column name
            description = f"{self.column_name}: {value}"
            descriptions.append(description)
            valid_values.append(value)
            
        # Generate embeddings for all descriptions
        embeddings = self.co.embed(
            texts=descriptions,
            model=MODEL_NAME,
            input_type='search_document'
        ).embeddings
        
        # Create upsert tuples
        for idx, (value, embedding) in enumerate(zip(valid_values, embeddings)):
            # Get all rows that have this value
            value_rows = batch_df[batch_df[self.column_name] == value]
            
            # Create metadata
            metadata = {
                'value': value,
                'column_name': self.column_name,
                'frequency': len(value_rows),
                'description': descriptions[idx],
                # Include additional statistics or metadata as needed
                'embedding_type': 'metadata'
            }
            
            # Create unique ID for this metadata value
            metadata_id = f"metadata_{self.column_name}_{value}".replace(" ", "_").lower()
            
            to_upsert.append((
                metadata_id,
                embedding,
                metadata
            ))
            
        return to_upsert

    def add_metadata(self, 
                     df: pd.DataFrame,
                     batch_size: int = 100) -> None:
        """
        Add metadata values from a DataFrame to the Pinecone index.
        Processes values in batches and creates embeddings for each unique value.
        
        Args:
            df: DataFrame containing the metadata column
            batch_size: Number of rows to process in each batch
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")
            
        if self.column_name not in df.columns:
            raise ValueError(f"Column '{self.column_name}' not found in DataFrame")
            
        # Calculate total number of batches
        total_batches = len(df) // batch_size + (1 if len(df) % batch_size != 0 else 0)
        
        # Process in batches
        for batch_start in tqdm(range(0, len(df), batch_size),
                              total=total_batches,
                              desc=f"Processing {self.column_name} metadata"):
            batch_end = min(batch_start + batch_size, len(df))
            batch_df = df.iloc[batch_start:batch_end]
            
            # Process the batch
            to_upsert = self._process_metadata_batch(batch_df)
            
            # Upsert to Pinecone if we have vectors
            if to_upsert:
                self.index.upsert(vectors=to_upsert)

    @lru_cache(maxsize=8)
    def calculate_query_embedding(self, query: str):
        """
        Calculate the query embedding for a given text query.
        
        Args:
            query: Text query to embed
            
        Returns:
            Query embedding vector
        """
        if query.startswith("data:image"):
            return self.co.embed(
                images=[query],
                model=MODEL_NAME,
                input_type='image'
            ).embeddings[0]
        else:
            return self.co.embed(
                texts=[query],
                input_type='search_query',
                model=MODEL_NAME
            ).embeddings[0]


    async def search_for_value_filters(
        self, 
        query: str, 
        top_k: int = 5,
        score_threshold: float = 0.6,
        existing_filters: Optional[Dict] = None
    ) -> Dict:
        """
        Generate Pinecone filters based on a text query for a specific column.
        
        Args:
            query: Search query from user
            top_k: Number of top values to consider for filtering
            score_threshold: Minimum similarity score to consider a match
            existing_filters: Optional existing filters to combine with
            
        Returns:
            Dict containing Pinecone-compatible filter
        """
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")

        query_embedding = self.calculate_query_embedding(query)

        # Query metadata vectors
        base_filter = {"embedding_type": {"$eq": "metadata"}}
        if existing_filters:
            base_filter.update(existing_filters)
            
        results = self.index.query(
            vector=query_embedding,
            filter=base_filter,
            top_k=top_k,
            include_metadata=True
        )

        # Analyze the matches
        value_scores = [(match.metadata['value'], match.score) 
                       for match in results.matches 
                       if match.score >= score_threshold]
        
        if not query.startswith("data:image"):
            vision_model = cl.user_session.get("vision_model")
            relevant_values = await vision_model.filter_metadata_filter(
                query=query,
                filter_category=self.column_name,
                filter_values=[v[0] for v in value_scores]
            )
            value_scores = [v for v in value_scores if v[0] in relevant_values]
        
        if len(value_scores) == 0:
            return None

        # If we have one high-confidence match
        if len(value_scores) == 1 and value_scores[0][1] > 0.7:
            return {self.column_name: {"$eq": value_scores[0][0]}}
        
        # Otherwise use multiple values
        return {self.column_name: {"$in": [v[0] for v in value_scores]}}

    @staticmethod
    def combine_filters(filters: List[Dict]) -> Dict:
        """
        Combine multiple filters using AND logic.
        
        Args:
            filters: List of individual filters to combine
            
        Returns:
            Combined filter dict
        """
        valid_filters = [f for f in filters if f is not None]
        if not valid_filters:
            return None
        if len(valid_filters) == 1:
            return valid_filters[0]
        return {"$and": valid_filters}


class ProductSearch:
    # Column mapping for YAML description
    COLUMN_TITLES = {
        'prod_name': 'Product Name',
        'detail_desc': 'Description',
        'colour_group_name': 'Color',
        'product_type_name': 'Product Type',
        'product_group_name': 'Product Group',
        'index_name': 'Category',
        'section_name': 'Department'
    }
    
    def __init__(self):
        """Initialize the ProductSearch system using environment variables."""
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.co = cohere.Client(COHERE_API_KEY)
        self.embedding_dimension = 384  # Cohere embed-multilingual-light-v3.0 dimension
        self.metadata_searchers = {}
        self.create_index()
        self.init_metadata_searchers()
        
    def create_index(self) -> None:
        """Create a new Pinecone index for products if it doesn't exist."""
        if PRODUCT_INDEX_NAME not in self.pc.list_indexes().names():
            self.pc.create_index(
                name=PRODUCT_INDEX_NAME,
                dimension=self.embedding_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud='aws',
                    region=AWS_REGION
                )
            )
        self.index = self.pc.Index(PRODUCT_INDEX_NAME)

    def _create_yaml_description(self, row: pd.Series) -> str:
        """Create a YAML-style description from product metadata."""
        yaml_parts = []
        for col, title in self.COLUMN_TITLES.items():
            if pd.notna(row[col]) and str(row[col]).strip():
                yaml_parts.append(f"{title}: {str(row[col]).strip()}")
        return '\n'.join(yaml_parts).strip()

    def _process_batch(self, 
                       batch_df: pd.DataFrame, 
                       images_dir: str) -> List[tuple]:
        """Process a batch of products and return vectors to upsert."""
        to_upsert = []
        
        # Prepare text embeddings batch
        valid_descriptions = []
        valid_indices = []
        
        for idx, row in batch_df.iterrows():
            yaml_desc = self._create_yaml_description(row)
            if yaml_desc:  # Only include if we have a valid description
                valid_descriptions.append(yaml_desc)
                valid_indices.append(idx)
        
        if len(valid_descriptions):
            print(valid_descriptions[0])
            text_embeddings = self.co.embed(
                texts=valid_descriptions,
                input_type='search_document',
                model=MODEL_NAME,
            ).embeddings
        
        # Prepare image embeddings batch
        valid_images = []
        image_indices = []
        
        # for idx, row in batch_df.iterrows():
        #     image_path = os.path.join(images_dir, f"0{row['article_id']}.jpg")
            
        #     if os.path.exists(image_path):
        #         processed_image = image_to_data_uri(image_path)
        #         valid_images.append(processed_image)
        #         image_indices.append(idx)
        
        # if valid_images:
        #     image_embeddings = []
        #     for img in valid_images:
        #         image_embeddings.extend(self.co.embed(
        #             model=MODEL_NAME,
        #             images=[img],
        #             input_type='image'
        #         ).embeddings)
        #         time.sleep(2.5)  # Sleep to avoid rate limiting
        
        # Create upsert tuples for text embeddings
        for embed_idx, df_idx in enumerate(valid_indices):
            row = batch_df.loc[df_idx]
            image_path = os.path.join(images_dir, f"0{row['article_id']}.jpg")
            metadata = {
                'article_id': str(row['article_id']),
                'product_code': str(row['product_code']),
                'prod_name': row['prod_name'],
                'detail_desc': row['detail_desc'],
                'colour_group_code': str(row['colour_group_code']),
                'colour_group_name': row['colour_group_name'],
                'product_type_no': str(row['product_type_no']),
                'product_type_name': row['product_type_name'],
                'product_group_name': row['product_group_name'],
                'index_code': str(row['index_code']),
                'index_name': row['index_name'],
                'index_group_no': str(row['index_group_no']),
                'index_group_name': row['index_group_name'],
                'section_no': str(row['section_no']),
                'section_name': row['section_name'],
                'yaml_description': self._create_yaml_description(row),
                'image': image_path,
            }
            
            to_upsert.append((
                f"text_{row['article_id']}", 
                text_embeddings[embed_idx],
                {**metadata, 'embedding_type': 'text'}
            ))
        
        # Create upsert tuples for image embeddings
        # for embed_idx, df_idx in enumerate(image_indices):
        #     row = batch_df.iloc[df_idx]
        #     metadata = {
        #         'article_id': str(row['article_id']),
        #         'product_code': str(row['product_code']),
        #         'prod_name': row['prod_name'],
        #         'detail_desc': row['detail_desc'],
        #         'colour_group_code': str(row['colour_group_code']),
        #         'colour_group_name': row['colour_group_name'],
        #         'product_type_no': str(row['product_type_no']),
        #         'product_type_name': row['product_type_name'],
        #         'product_group_name': row['product_group_name'],
        #         'index_code': str(row['index_code']),
        #         'index_name': row['index_name'],
        #         'index_group_no': str(row['index_group_no']),
        #         'index_group_name': row['index_group_name'],
        #         'section_no': str(row['section_no']),
        #         'section_name': row['section_name'],
        #         'yaml_description': self._create_yaml_description(row),  # Store the YAML description in metadata
        #         'image': valid_images[df_idx],
        #     }
            
        #     to_upsert.append((
        #         f"image_{row['article_id']}", 
        #         image_embeddings[embed_idx],
        #         {**metadata, 'embedding_type': 'image'}
        #     ))
            
        return to_upsert
    
    def add_products(self, 
                     products_df: pd.DataFrame, 
                     images_dir: str,
                     batch_size: int = 100) -> None:
        """
        Add products to the index from a DataFrame and corresponding images.
        Processes embeddings and uploads in batches.
        
        Args:
            products_df: DataFrame with product metadata
            images_dir: Directory containing product images named as article_id.jpg
            batch_size: Number of products to process in each batch
        """
        total_batches = len(products_df) // batch_size + (1 if len(products_df) % batch_size != 0 else 0)
        
        for batch_start in tqdm(range(0, len(products_df), batch_size), 
                              total=total_batches,
                              desc="Processing product batches"):
            batch_end = min(batch_start + batch_size, len(products_df))
            batch_df = products_df.iloc[batch_start:batch_end]
            
            # Process the batch to get vectors to upsert
            to_upsert = self._process_batch(batch_df, images_dir)
            
            # Upsert to Pinecone if we have vectors
            if to_upsert:
                self.index.upsert(vectors=to_upsert)


    def init_metadata_searchers(self):
        """
        Initialize metadata searchers for relevant columns
        """
        for column in [
            'colour_group_name',
            'product_type_name',
            'product_group_name',
            'index_name',
            'section_name'
        ]:
            searcher = MetadataSearch(column_name=column)
            self.metadata_searchers[column] = searcher
    
    async def generate_filters_from_query(
        self,
        query: str,
        top_k: int = 8,
        score_threshold: float = 0.2
    ) -> Optional[Dict]:
        """
        Generate combined filters from a query across all metadata columns.
        
        Args:
            query: User search query
            top_k: Number of top values to consider per column
            score_threshold: Minimum similarity score to consider
            
        Returns:
            Combined filter dict for Pinecone query
        """
        if not self.metadata_searchers:
            raise ValueError("Metadata searchers not initialized. Call init_metadata_searchers() first.")

        filters = []

        for searcher in self.metadata_searchers.values():
            column_filter = searcher.search_for_value_filters(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold
            )
            filters.append(column_filter)

        filters = [
            filt for filt in await asyncio.gather(*filters) if filt is not None
        ]
        return MetadataSearch.combine_filters(filters)
