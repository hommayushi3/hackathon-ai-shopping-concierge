import Link from "next/link";
import { getProductImage, getProductInfo, getProductLink } from "../../lib/product";

function ReviewCartItem({ id, product }) {
  if (!product) {
    product = getProductInfo(0);
  }
  return (
    <div className="d-flex">
      <div className="flex-shink-0">
        <img
          className="rounded"
          src={getProductImage(id)}
          width={80}
          height={80}
          alt="Product image."
          style={{ objectFit: "cover" }}
        />
      </div>
      <div className="flex-grow-1 ms-3 h-100">
        <div className="vstack">
          <Link legacyBehavior href={getProductLink(id)}>
            <a className="text-dark text-decoration-none">{product.productName}</a>
          </Link>
          <small className="text-muted mb-2" style={{ fontSize: 12 }}>
            <span>Medium</span>
            ,&nbsp;
            <span>{product.color}</span>
          </small>
          <h6 className="mb-0">1 &times; {product.price}</h6>
        </div>
      </div>
    </div>
  );
}

export default ReviewCartItem;
