import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Carousel } from "react-responsive-carousel";
import ProductSimpleCard from "../components/product/product-simple-card";
import { useState, useEffect } from "react";
import { getDb, formatPrice } from "../lib/product";

export default function Home() {
  const [isLoaded, setLoaded] = useState(false);
  const [db, setResult] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!isLoaded) {
        const newData = await getDb();
        setResult(() => newData);
        setLoaded(true);
      }
    };
    fetchData().catch((e) => {
      console.error(`failed to fetch data: ${e}`);
    });
  }, [db, setResult, isLoaded, setLoaded]);

  return (
    <div>
      <div className="container py-3">
        <div className="row mb-4">
          <div className="col-12">
            <Carousel
              autoPlay={true}
              infiniteLoop={true}
              showArrows={false}
              showStatus={false}
              showThumbs={false}
              transitionTime={500}
              renderIndicator={(onClickHandler, isSelected, index, label) => {
                if (isSelected) {
                  return (
                    <li className="d-inline-block m-2 text-light">
                      <FontAwesomeIcon icon={["fas", "circle"]} size="xs" />
                    </li>
                  );
                }
                return (
                  <li
                    className="d-inline-block m-2 text-light text-opacity-50"
                    onClick={onClickHandler}
                    key={index}
                    role="button"
                    tabIndex={0}
                  >
                    <FontAwesomeIcon icon={["fas", "circle"]} size="xs" />
                  </li>
                );
              }}
            >
              {
                [1, 2, 3].map((i) => {
                  return (<div>
                    <img
                      src={`/data/front_page_slider_${i}.jpg`}
                      alt="Cover image"
                      className="rounded"
                    />
                  </div>)
                })
              }
            </Carousel>
          </div>
        </div>
        <div className="row row-cols-1 row-cols-md-3 g-3 mb-4">
          <div className="col">
            <div className="card h-100 border-0 shadow-sm">
              <figure className="figure card-body mb-0">
                <div
                  className="bg-secondary rounded-circle d-flex mb-2"
                  style={{ width: 50, height: 50 }}
                >
                  <FontAwesomeIcon
                    icon={["fas", "money-bill-alt"]}
                    size="lg"
                    className="text-primary m-auto"
                  />
                </div>
                <h5 className="mb-1 fw-bold">Reasonable Price</h5>
                <figcaption className="figure-caption text-dark">
                  Shop confidently with our competitively priced fashion collections. We believe great style shouldn't break the bank, offering quality clothing at prices that make sense. From everyday basics to seasonal trends, find your perfect look without compromising your budget.
                </figcaption>
              </figure>
            </div>
          </div>
          <div className="col">
            <div className="card h-100 border-0 shadow-sm">
              <figure className="figure card-body mb-0">
                <div
                  className="bg-secondary rounded-circle d-flex mb-2"
                  style={{ width: 50, height: 50 }}
                >
                  <FontAwesomeIcon
                    icon={["fas", "headset"]}
                    size="lg"
                    className="text-primary m-auto"
                  />
                </div>
                <h5 className="mb-1 fw-bold">Customer Support 24/7</h5>
                <figcaption className="figure-caption text-dark">
                  Have questions? We're here around the clock to help! Our dedicated support team is ready to assist with sizing guidance, order tracking, or any other concerns. Whether it's midnight or midday, reach out via chat, email, or phone. Your satisfaction is our priority, backed by our hassle-free return policy.
                </figcaption>
              </figure>
            </div>
          </div>
          <div className="col">
            <div className="card h-100 border-0 shadow-sm">
              <figure className="figure card-body mb-0">
                <div
                  className="bg-secondary rounded-circle d-flex mb-2"
                  style={{ width: 50, height: 50 }}
                >
                  <FontAwesomeIcon
                    icon={["fas", "truck"]}
                    size="lg"
                    className="text-primary m-auto"
                  />
                </div>
                <h5 className="mb-1 fw-bold">Fast Delivery</h5>
                <figcaption className="figure-caption text-dark">
                  Get your new favorite pieces faster with our swift shipping service. Most orders ship within 24 hours, and we offer multiple delivery options to suit your needs. Track your package every step of the way, and enjoy free shipping on orders over a certain value. Because great style shouldn't keep you waiting.                </figcaption>
              </figure>
            </div>
          </div>
        </div>
        <h4 className="mb-3 fw-semibold">New products</h4>
        <div className="row row-cols-1 row-cols-sm-2 row-cols-lg-4 g-3 mb-5">
          {
            db &&
            Object.keys(db).slice(0, 12).map((id) => {
              const productName = isLoaded ? db[id]['prod_name'] : `Product ${id}`;
              const price = isLoaded ? formatPrice(db[id]['price']) : 0;
              return (
                <div className="col" key={id}>
                  <ProductSimpleCard id={id} productName={productName} price={price} />
                </div>
              );
            })}
        </div>
      </div>
      {/* <div className="d-flex flex-column align-items-center bg-primary py-5">
        <span className="mb-4 text-light text-opacity-75">
          Subscribe for promotions and wonderful events
        </span>
        <form className="d-flex">
          <div className="me-2">
            <input
              type="email"
              className="form-control"
              placeholder="Your email"
              size="24"
            />
          </div>
          <button className="btn btn-warning">
            <FontAwesomeIcon icon={["fas", "envelope"]} className="me-2" />
            Subscribe
          </button>
        </form>
      </div> */}
    </div>
  );
}
