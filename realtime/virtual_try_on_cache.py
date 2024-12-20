from json import dumps, loads
import hashlib
import requests
import redis
from typing import Dict, Any, Optional
import os
import zlib

REDIS_URL = "redis-11713.c60.us-west-1-2.ec2.redns.redis-cloud.com"


class RedisCache:
    def __init__(
        self,
        redis_url: str = REDIS_URL,
        ttl_seconds: int = 3600 * 24,
        prefix: str = "api_cache:",
        compression_threshold: int = 1000000000,  # Compress responses larger than 1KB
        max_item_size: int = 500_000_000  # 500KB max per item to be safe
    ):
        """
        Initialize Redis cache optimized for free tier usage.
        
        Args:
            redis_url: Redis connection URL from Redis Cloud
            ttl_seconds: Cache TTL in seconds
            prefix: Key prefix for cache entries
            compression_threshold: Compress items larger than this (bytes)
            max_item_size: Maximum size for cached items (bytes)
        """
        # Use a single connection pool to stay within connection limits
        self.redis_client = redis.Redis(
            host=redis_url,
            port=11713,
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=False,  # Need binary for compression
            max_connections=5  # Keep pool small for free tier
        )
        self.ttl_seconds = ttl_seconds
        self.prefix = prefix
        self.compression_threshold = compression_threshold
        self.max_item_size = max_item_size

    def _generate_cache_key(self, data: Dict[str, Any], headers: Dict[str, str]) -> str:
        """Generate a compact cache key."""
        headers_copy = headers.copy()
        headers_copy.pop('x-api-key', None)
        
        # Only include essential fields in cache key to save space
        cache_data = {
            'data': {k: v for k, v in data.items() if k not in ['model_image', 'base64']},
            'headers': headers_copy
        }
        return f"{self.prefix}{hashlib.md5(dumps(cache_data, sort_keys=True).encode()).hexdigest()}"

    def _compress_data(self, data: bytes) -> bytes:
        """Compress data with a flag prefix."""
        return b'1' + zlib.compress(data)

    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data if it was compressed."""
        if data.startswith(b'1'):
            return zlib.decompress(data[1:])
        return data[1:]

    def get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get and decompress cached response."""
        try:
            data = self.redis_client.get(cache_key)
            if data is None:
                return None
                
            # decompressed = self._decompress_data(data)
            return data
        except Exception:
            import traceback
            traceback.print_exc()
            return None

    def cache_response(
        self, 
        cache_key: str, 
        response_data: Dict[str, Any],
    ) -> bool:
        """Cache response with compression if needed."""
        try:
            # Serialize the response data
            data = response_data
            
            # Skip if data is too large
            if len(data) > self.max_item_size:
                return False
                
            # Add compression flag and possibly compress
            # if len(data) > self.compression_threshold:
            #     data = self._compress_data(data)
            # else:
            #     data = b'0' + data
                
            # Use pipeline for atomic operation
            pipe = self.redis_client.pipeline()
            pipe.set(cache_key, data, ex=self.ttl_seconds)
            
            # Simple memory management
            if len(data) > 100_000:  # For large items
                pipe.delete(
                    self.redis_client.random_key()  # Make space if needed
                )
            
            pipe.execute()
            return True
            
        except Exception:
            return False

    def make_cached_request(
        self, 
        url: str, 
        json: Dict[str, Any], 
        headers: Dict[str, str]
    ) -> requests.Response:
        """Make API request with caching."""
        cache_key = self._generate_cache_key(json, headers)
        
        # Try to get from cache
        cached_response = self.get_cached_response(cache_key)
        if cached_response is not None:
            response = requests.Response()
            response._content = cached_response
            response.status_code = 200
            return response
        
        # Make actual API request
        response = requests.post(url, json=json, headers=headers)
        
        # Cache successful responses
        if response.status_code == 200:
            try:
                response_data = response.content
                self.cache_response(cache_key, response_data)
            except Exception:
                import traceback
                traceback.print_exc()
                pass
        
        return response

    def clear_old_entries(self, keep_last_n: int = 100) -> int:
        """
        Clear old entries to free up space.
        Returns number of entries cleared.
        """
        try:
            # Get all keys with our prefix
            keys = self.redis_client.keys(f"{self.prefix}*")
            if len(keys) <= keep_last_n:
                return 0
                
            # Sort keys by last access time
            keys_with_time = [
                (k, self.redis_client.object('idletime', k))
                for k in keys
            ]
            keys_with_time.sort(key=lambda x: x[1], reverse=True)
            
            # Delete oldest keys
            to_delete = keys_with_time[keep_last_n:]
            if to_delete:
                self.redis_client.delete(*[k[0] for k in to_delete])
                return len(to_delete)
            return 0
            
        except Exception:
            return 0

    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache usage information."""
        try:
            info = self.redis_client.info()
            return {
                'used_memory_bytes': info.get('used_memory', 0),
                'total_keys': len(self.redis_client.keys(f"{self.prefix}*")),
                'connected_clients': info.get('connected_clients', 0)
            }
        except Exception:
            return {}


if __name__ == '__main__':
    from realtime.vision import image_to_data_uri
    from realtime.virtual_try_on import MODEL_IMAGE_PATH, SEGMIND_API_BASE

    cloth_image = "data/product_catalog_images/0108775015.jpg"
    category = "Upper body"
    num_inference_steps = 35
    guidance_scale = 2
    base64 = True
    seed = 0

    SEGMIND_API_KEY = os.getenv("SEGMIND_API_KEY")
    redis_cache = RedisCache()
    model_image = image_to_data_uri(MODEL_IMAGE_PATH).split(",")[1]

    data = {
        "model_image": model_image,
        "cloth_image": image_to_data_uri(cloth_image).split(",")[1],
        "category": category,
        "num_inference_steps": num_inference_steps,
        "guidance_scale": guidance_scale,
        "base64": base64
    }
    if seed is not None:
        data["seed"] = seed
    headers = {'x-api-key': SEGMIND_API_KEY}
    response = redis_cache.make_cached_request(SEGMIND_API_BASE, json=data, headers=headers)
    # print(response.json())
