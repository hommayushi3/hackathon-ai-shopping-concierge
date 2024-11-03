import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Link from "next/link";
import { getCheckoutLink, getProductImage, getProductLink } from "../../lib/product";
import { useRouter } from 'next/navigation'

function ProductGridCard({ id, product, off }) {
  const router = useRouter();

  let price = 10000;
  let percentOff;
  let offPrice = `${price}Ks`;

  if (off && off > 0) {
    percentOff = (
      <div
        className="badge bg-dark opacity-75 py-2 text-white position-absolute"
        style={{ top: "0.5rem", right: "0.5rem" }}
      >
        {off}% OFF
      </div>
    );

    offPrice = (
      <>
        {price - (off * price) / 100}Ks&nbsp;
        <del className="text-muted small fw-normal">{price}Ks</del>
      </>
    );
  }
  return (
    <div className="card h-100 border-0 shadow-sm">
      <Link legacyBehavior href={getProductLink(id)}>
        <a>
          <div className="ratio ratio-1x1">
            <img
              className="card-img-top "
              src={getProductImage(id)}
              alt="Product image."
              style={{ objectFit: "cover" }}
            />
          </div>
          {percentOff}
        </a>
      </Link>
      <div className="card-body">
        <div className="vstack gap-2">
          <Link legacyBehavior href={getProductLink(id)}>
            <a className="text-dark text-decoration-none">{product.productName}</a>
          </Link>

          <h6 className="fw-semibold">{product.price}</h6>

          <div className="hstack gap-2">
            {/* <button className="btn btn-secondary text-primary flex-grow-1 d-md-block d-lg-none">
              <FontAwesomeIcon icon={["fas", "cart-plus"]} />
              &nbsp;Buy now
            </button>
            <button className="btn btn-outline-secondary text-primary border d-md-block d-lg-none">
              <FontAwesomeIcon icon={["far", "heart"]} />
            </button> */}

            <button
              className="btn btn-sm btn-secondary text-primary flex-grow-1 d-none d-lg-block"
              onClick={() => router.push(getCheckoutLink(product.id))}>
              <FontAwesomeIcon icon={["fas", "cart-plus"]} />
              &nbsp;Buy now
            </button>
            <button className="btn btn-sm btn-outline-secondary text-primary border d-none d-lg-block">
              <FontAwesomeIcon icon={["far", "heart"]} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductGridCard;
