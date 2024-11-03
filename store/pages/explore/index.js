import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import ProductGridCard from "../../components/product/product-grid-card";
import { useState, useEffect } from "react";
import { getDb, getProductInfo } from "../../lib/product";
import { useSearchParams } from 'next/navigation';

function ExploreProducts() {
  const categories = ['Ladieswear', 'Menswear', 'Sport', 'Divided', 'Baby/Children'];
  
  const [isLoaded, setLoaded] = useState(false);
  const [db, setResult] = useState(null);
  const [filteredProducts, setFilteredProducts] = useState([]);

  const searchParams = useSearchParams();
  const category = searchParams.get('cat') || 'all';
  const articleIds = searchParams.get('article_ids')?.split(',') || [];

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch the entire database if it's not already loaded
        const newData = await getDb();
        setResult(newData);
        
        // Filter products based on `articleIds`
        const matchingProducts = articleIds.length === 0
          ? Object.values(newData) // Load all products if `articleIds` is empty
          : articleIds.map(id => newData[id]).filter(Boolean); // Load specific products

        setFilteredProducts(matchingProducts);
        setLoaded(true);
      } catch (e) {
        console.error(`failed to fetch data: ${e}`);
      }
    };

    fetchData();
  }, [articleIds]);

  let matching = [];
  let products = [];
  if (isLoaded) {
    matching = filteredProducts.filter((product) => {
      return category === 'all' || product['index_group_name'] === category;
    });
    products = matching.slice(0, 9).map((p) => getProductInfo(p));
  }

  return (
    <div className="vstack">
      <div className="bg-secondary">
        <div className="container">
          <div className="row py-4 px-2">
            <nav aria-label="breadcrumb col-12">
              <ol className="breadcrumb mb-1">
                <li className="breadcrumb-item">
                  <a href="/explore?cat=all">All Categories</a>
                </li>
                {
                  category !== 'all' && <li className="breadcrumb-item">
                    <a href="#">{category}</a>
                  </li>
                }
              </ol>
            </nav>
          </div>
        </div>
      </div>
      <div className="container py-4">
        <div className="row g-3">
          <div className="col-lg-3">
            {/* Categories and Filters */}
          </div>
          <div className="col-lg-9">
            <div className="hstack justify-content-between mb-3">
              <span className="text-dark">
                {isLoaded ? `${matching.length} items found` : "Loading..."}
              </span>
              <div className="btn-group" role="group">
                <button className="btn btn-outline-dark">
                  <FontAwesomeIcon icon={["fas", "sort-amount-up"]} />
                </button>
                <button className="btn btn-outline-dark">
                  <FontAwesomeIcon icon={["fas", "th-list"]} />
                </button>
              </div>
            </div>
            <div className="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-3">
              {products.map((product) => {
                return (
                  <div key={product.id} className="col">
                    <ProductGridCard id={product.id} product={product} />
                  </div>
                );
              })}
            </div>
            <nav className="float-end mt-3">
              <ul className="pagination">
                <li className="page-item">
                  <a className="page-link" href="#">
                    Prev
                  </a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">
                    1
                  </a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">
                    2
                  </a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">
                    3
                  </a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">
                    Next
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ExploreProducts;