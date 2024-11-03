import Link from "next/link";
import ProductRating from "../product-rating";
import { getProductImage, getProductLink } from "../../lib/product";

function ProductSimpleCard({ id, product }) {
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
        <Link legacyBehavior href={getProductLink(id)}>
          <a className="mb-1 text-dark text-decoration-none stretched-link">
            {product.productName}
          </a>
        </Link>
        &nbsp;&nbsp;
        <span className="text-muted small">{product.color}</span>

        <ProductRating />

        <h6 className="mb-0 fw-semibold mt-2">{product.price}</h6>
      </div>
    </div>
  );
}

export default ProductSimpleCard;
