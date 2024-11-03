import Link from "next/link";
import ProductRating from "../product-rating";
import {getProductImage} from "../../lib/product";

function ProductSimpleCard({ id, productName, price }) {
  return (
    <div className="card h-100 border-0 shadow-sm">
      <div className="ratio ratio-1x1">
        <img
          className="card-img-top"
          src={getProductImage(id)}
          alt="Product image."
          style={{ objectFit: "cover" }}
        />
      </div>
      <div className="card-body">
        <Link legacyBehavior href="/product/1">
          <a className="mb-1 text-dark text-decoration-none stretched-link">
            {productName}
          </a>
        </Link>

        <ProductRating />

        <h6 className="mb-0 fw-semibold mt-2">${price}</h6>
      </div>
    </div>
  );
}

export default ProductSimpleCard;
