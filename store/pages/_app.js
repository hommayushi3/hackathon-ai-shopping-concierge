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

config.autoAddCss = false;
library.add(fab, fas, far);

if (typeof window !== "undefined") {
  require("bootstrap/dist/js/bootstrap.bundle.min.js");
}

function MyApp({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    function addChainlitCopilot() {
      // Check if the script is already added to avoid duplicating it
      if (!document.querySelector(`script[src="http://localhost:8000/copilot/index.js"]`)) {
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
      console.log("You sent: " + JSON.stringify(args));

      // Prepare article_ids as a query parameter if available
      const articleIds = args.article_ids ? args.article_ids.join(',') : '';

      // Redirect to /explore with article_ids in the query string
      router.push(`/explore?article_ids=${articleIds}`);
    }

    addChainlitCopilot();

    return () => {
      // Remove the event listener on unmount
      window.removeEventListener("chainlit-call-fn", handleChainlitEvent);

      // Remove the script from the document
      const scriptElement = document.querySelector(`script[src="http://localhost:8000/copilot/index.js"]`);
      if (scriptElement) document.body.removeChild(scriptElement);
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