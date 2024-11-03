import "../styles/bootstrap-custom.css";
import "../styles/globals.css";
import "react-responsive-carousel/lib/styles/carousel.min.css";
import { config, library } from "@fortawesome/fontawesome-svg-core";
import "@fortawesome/fontawesome-svg-core/styles.css";
import { fab } from "@fortawesome/free-brands-svg-icons";
import { fas } from "@fortawesome/free-solid-svg-icons";
import { far } from "@fortawesome/free-regular-svg-icons";
import Layout from "../components/layout";
import { useEffect } from 'react';
import { useRouter } from 'next/router';
import { getCheckoutLink, getProductLink } from "../lib/product";

config.autoAddCss = false;
library.add(fab, fas, far);

if (typeof window !== "undefined") {
  require("bootstrap/dist/js/bootstrap.bundle.min.js");
}

let chainlitInitialized = false; // Track initialization status

function MyApp({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    function addChainlitCopilot() {
      if (!chainlitInitialized) {
        chainlitInitialized = true; // Mark Chainlit as initialized

        // Add the script only once
        const myScript = document.createElement('script');
        myScript.src = "http://localhost:8000/copilot/index.js";
        document.body.appendChild(myScript);

        // Set up the event listener after the script loads
        myScript.onload = () => {
          window.addEventListener("chainlit-call-fn", handleChainlitEvent);

          // Initialize the Chainlit widget
          window.mountChainlitWidget({
            chainlitServer: "http://localhost:8000",
          });
        };
      }
    }

    function handleChainlitEvent(e) {
      const { name, args, callback } = e.detail;
      callback("You sent: " + args.msg);
      console.log(`Received chainlit event: ${name} ${JSON.stringify(args)}`);

      // Prepare article_ids as a query parameter if available
      const articleIds = args.article_ids ? args.article_ids.join(',') : '';

      if (name === "recommendations") {
        // Redirect to /explore with article_ids in the query string
        router.push(`/explore?article_ids=${articleIds}`);
      } else if (name === "update_cart") {
        router.push(getCheckoutLink(articleIds));
      } else if (name === "try_on") {
        router.push(getProductLink(articleIds));
      } else {
        console.error("unrecognize action " + name);
      }
    }

    addChainlitCopilot();

    return () => {
      // Clean up event listener only
      window.removeEventListener("chainlit-call-fn", handleChainlitEvent);
    };
  }, [router]);

  const getLayout = Component.getLayout;
  if (getLayout) {
    return getLayout(<Component {...pageProps} />);
  }

  return (
    <Layout>
      <Component {...pageProps} />
    </Layout>
  );
}

export default MyApp;