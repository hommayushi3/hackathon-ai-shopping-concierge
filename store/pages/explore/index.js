import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import ProductGridCard from "../../components/product/product-grid-card";
import { useState, useEffect } from "react";
import { getDb, getProductInfo } from "../../lib/product";
import { useSearchParams } from 'next/navigation';

function ExploreProducts() {
  const categories = ['Ladieswear', 'Menswear', 'Sport', 'Divided', 'Baby/Children'];
  const productTypes = [
    'Garment Upper body',
    'Garment Lower body',
    'Accessories',
    'Socks & Tights',
    'Underwear',
    'Shoes',
    'Garment Full body',
    'Nightwear',
    'Swimwear',
    // 'Unknown',
    // 'Bags',
    // 'Items',
    // 'Furniture'
  ];
  const typeState = new Map();
  let matchingPType = new Map();
  for (let pType of productTypes) {
    typeState[pType] = useState(true);
    matchingPType[pType] = 0;
  }

  const [isLoaded, setLoaded] = useState(false);
  const [db, setResult] = useState(null);

  const searchParams = useSearchParams();
  const category = searchParams.get('cat') || 'all';
  const articleIds = searchParams.get('article_ids')?.split(',') || [];
  console.log('loaded explore page with items ' + articleIds);

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!isLoaded) {
          const newData = await getDb();
          setResult(() => newData);
          setLoaded(true);
        }
      } catch (e) {
        console.error(`failed to fetch data: ${e}`);
      }
    };

    fetchData();
  }, [db, setResult, isLoaded, setLoaded]);

  let matching = [];
  let products = [];

  const findMatching = () => {
    const cols = ['product_group_name', 'product_type_name', 'section_name'];
    const s = cols.map((col) => new Set());
    if (isLoaded) {
      matching = Object.entries(db).filter(([k, v]) => {
        const categoryMatch = category === 'all' || v['index_group_name'] === category;
        const state = typeState[v['product_group_name']];
        const typeMatch = state ? state[0] : false;
        const articleMatch = articleIds.length === 0 || articleIds.includes(k);
        if (categoryMatch) {
          matchingPType[v['product_group_name']]++;
        }
        // console.log(`${k} ${categoryMatch} ${typeMatch} ${articleMatch}`);
        return categoryMatch && typeMatch && articleMatch;
      }).map(([k, v]) => v);
      products = matching.slice(0, 9).map((p) => getProductInfo(p));
      // console.log(products);
      // console.log(s);
      // console.log(matchingPType);
    }
  };
  findMatching();

  const onTypeChange = (pType, e) => {
    typeState[pType][1](e.target.checked);
    // console.log(typeState);
    findMatching();
  };

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
            <div className="accordion shadow-sm rounded">
              <div className="accordion-item border-bottom">
                <h2 className="accordion-header">
                  <button
                    className="accordion-button fw-bold"
                    data-bs-toggle="collapse"
                    data-bs-target="#collapseOne"
                    aria-expanded="true"
                  >
                    Categories
                  </button>
                </h2>
                <div
                  id="collapseOne"
                  className="accordion-collapse collapse show"
                >
                  <div className="accordion-body pt-2">
                    <div className="vstack gap-2">
                      {
                        categories.map((category) => {
                          return (<a
                            key={`a-${category}`}
                            href={`/explore?cat=${category}`}
                            className="fw-medium link-dark text-decoration-none"
                          >
                            {category}
                          </a>);
                        })
                      }
                    </div>
                  </div>
                </div>
              </div>
              <div className="accordion-item border-bottom">
                <h2 className="accordion-header">
                  <button
                    className="accordion-button fw-bold"
                    data-bs-toggle="collapse"
                    data-bs-target="#collapseTwo"
                    aria-expanded="true"
                  >
                    Product type
                  </button>
                </h2>
                <div
                  id="collapseTwo"
                  className="accordion-collapse collapse show"
                >
                  <div className="accordion-body pt-2">
                    <div className="vstack gap-2">
                      {
                        productTypes.map((pType) => {
                          return (<div key={`div-${pType}`} className="d-flex gap-2">
                            <input
                              id={`input-${pType}`}
                              type="checkbox"
                              className="form-check-input"
                              checked={typeState[pType][0]}
                              onChange={(e) => onTypeChange(pType, e)} />
                            <label className="fw-medium flex-grow-1">{pType}</label>
                            <span className="badge bg-default rounded-pill my-auto mb-0 text-dark">
                              {matchingPType[pType]}
                            </span>
                          </div>);
                        })
                      }
                    </div>
                  </div>
                </div>
              </div>
              <div className="accordion-item">
                <h2 className="accordion-header">
                  <button
                    className="accordion-button fw-bold"
                    data-bs-toggle="collapse"
                    data-bs-target="#collapseThree"
                    aria-expanded="true"
                  >
                    Price Range
                  </button>
                </h2>
                <div
                  id="collapseThree"
                  className="accordion-collapse collapse show"
                >
                  <div className="accordion-body pt-0">
                    <form className="row g-3">
                      <div className="col-6">
                        <label className="form-label">Min</label>
                        <input type="text" className="form-control" />
                      </div>
                      <div className="col-6">
                        <label className="form-label">Max</label>
                        <input type="text" className="form-control" />
                      </div>
                      <div className="col-12">
                        <button className="btn btn-primary w-100">Apply</button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            </div>
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
              {products.map((product) => (
                <div key={product.id} className="col">
                  <ProductGridCard id={product.id} product={product} />
                </div>
              ))}
            </div>
            <nav className="float-end mt-3">
              <ul className="pagination">
                <li className="page-item">
                  <a className="page-link" href="#">Prev</a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">1</a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">2</a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">3</a>
                </li>
                <li className="page-item">
                  <a className="page-link" href="#">Next</a>
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