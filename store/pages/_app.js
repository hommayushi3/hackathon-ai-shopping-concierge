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

config.autoAddCss = false;
library.add(fab, fas, far);

if (typeof window !== "undefined") {
  require("bootstrap/dist/js/bootstrap.bundle.min.js");
}

function addChainlitCopilot() {
  // https://docs.chainlit.io/deploy/copilot
  const myScript = document.createElement('script');
  myScript.src = "http://localhost:8000/copilot/index.js";
  document.body.appendChild(myScript);
  myScript.onload = () => {
    window.addEventListener("chainlit-call-fn", (e) => {
      const { name, args, callback } = e.detail;
      callback("You sent: " + args.msg);
    });
    window.mountChainlitWidget({
      chainlitServer: "http://localhost:8000",
    });
  };
}

function MyApp({ Component, pageProps }) {
  useEffect(addChainlitCopilot, []);

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
