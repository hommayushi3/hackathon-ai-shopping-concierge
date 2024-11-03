import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Link from "next/link";
import { formatPrice } from "../../lib/product";

function PricingCard({ data, pricingOnly, children, subtotal }) {
  const deliveryCharge = 5;
  return (
    <div className="card border-0 shadow-sm">
      <div className="card-body">
        <div className="vstack gap-2">
          <div className="d-flex justify-content-between">
            <span>Subtotal:</span>
            <span>{formatPrice(subtotal)}</span>
          </div>
          <div className="d-flex justify-content-between">
            <span>Discount:</span>
            <span className="text-danger">-</span>
          </div>
          <div className="d-flex justify-content-between">
            <span>Delivery charge:</span>
            <span className="text-success">+{formatPrice(deliveryCharge)}</span>
          </div>

          <hr className="text-muted" />

          <div className="d-flex justify-content-between">
            <span className="h5">Total:</span>
            <span className="fw-bold h5 mb-0">{formatPrice(subtotal + deliveryCharge)}</span>
          </div>

          {!pricingOnly && (
            <div className="d-grid gap-2 mt-2">
              <Link legacyBehavior href="/checkout/delivery-info">
                <a className="btn btn-primary">Checkout</a>
              </Link>
              <Link legacyBehavior href="/">
                <a className="btn btn-outline-primary">Continue Shopping</a>
              </Link>
            </div>
          )}
          {children}
        </div>
      </div>
    </div>
  );
}

export default PricingCard;
