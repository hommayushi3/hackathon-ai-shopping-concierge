import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState, useEffect } from "react";
import { getDb, getProductInfo } from "../../lib/product";
import { useSearchParams } from 'next/navigation';

const stepClass =
  "p-0 position-absolute rounded-circle btn btn-primary fw-bold";

function CheckoutStepper({ step = 1 }) {
  let progress = 0;
  if (step == 2) {
    progress = 50;
  } else if (step == 3) {
    progress = 100;
  }

  const [isLoaded, setLoaded] = useState(false);
  const [db, setResult] = useState(null);

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

  const searchParams = useSearchParams();
  const articleIds = searchParams.get('article_ids')?.split(',') || [];

  let matching = [];
  let products = [];
  if (isLoaded) {
    matching = Object.entries(db).filter(([k, v]) => {
      const articleMatch = articleIds.length === 0 || articleIds.includes(k);
      return articleMatch;
    }).map(([k, v]) => v);
    products = matching.map((p) => getProductInfo(p));
    // console.log(products);
    // console.log(s);
  }

  return (
    <>
      <div className="position-relative mt-3 mb-4 mx-5 text-light">
        <div className="progress" style={{ height: 6 }}>
          <div
            className="progress-bar"
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin="0"
            aria-valuemax="100"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <button
          disabled={step < 1}
          className={stepClass + " top-50 start-0 translate-middle"}
          style={{ width: 40, height: 40 }}
        >
          <FontAwesomeIcon icon={["fas", step > 1 ? "check" : "truck"]} />
        </button>
        <button
          disabled={step < 2}
          className={stepClass + " top-50 start-50 translate-middle"}
          style={{ width: 40, height: 40 }}
        >
          <FontAwesomeIcon icon={["fas", step > 2 ? "check" : "credit-card"]} />
        </button>
        <button
          disabled={step < 3}
          className={stepClass + " top-50 start-100 translate-middle"}
          style={{ width: 40, height: 40 }}
        >
          <FontAwesomeIcon
            icon={["fas", step > 3 ? "check" : "clipboard-check"]}
          />
        </button>
      </div>
      <div className="position-relative mb-4 mx-5" style={{ height: 20 }}>
        <span className="position-absolute top-50 start-0 translate-middle">
          Delivery
        </span>
        <span className="position-absolute top-50 start-50 translate-middle">
          Payment
        </span>
        <span className="position-absolute top-50 start-100 translate-middle">
          Confirmation
        </span>
      </div>
    </>
  );
}

export default CheckoutStepper;
