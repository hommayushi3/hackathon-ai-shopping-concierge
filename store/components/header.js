import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Link from "next/link";

function Header({ simple, hideAuth }) {
  let title = process.env.APP_NAME;
  const categories = ['Ladieswear', 'Menswear', 'Sport', 'Divided', 'Baby/Children'];
  return (
    <header>
      <nav className="navbar navbar-expand-lg navbar-light bg-white border-bottom">
        <div className="container">
          <Link legacyBehavior href="/">
            <a className="navbar-brand">
              {/* <FontAwesomeIcon
                icon={["fas", "shopping-basket"]}
                className="d-inline-block"
              /> */}
              <span className="ms-2 mb-0 h4 text-primary fw-bold">
                Uniqbro
              </span>
            </a>
          </Link>
          <div className="collapse navbar-collapse">
            <form className="d-flex">
              <div className="input-group">
                <input
                  className="form-control"
                  type="search"
                  placeholder="Search..."
                  aria-label="Search"
                  size="32"
                />
                <button type="button" className="btn btn-primary">
                  <FontAwesomeIcon icon={["fas", "search"]} />
                </button>
              </div>
            </form>
          </div>
          <div className="d-flex">
            <img src="/data/person-icon1.png"
              width={30}
              height={30}
            />
            <div>
              <div className="position-relative ms-2 fw-normal" style={{ "vertical-align": "middle" }}>
                Welcome, Patrick
              </div>
              {/* <Link legacyBehavior href="/auth/login">
                <a className="btn btn-outline-primary d-none d-md-block">
                  Login
                </a>
              </Link>
              <Link legacyBehavior href="/auth/sign-up">
                <a className="btn btn-primary d-none d-md-block ms-2">
                  Sign up
                </a>
              </Link> */}
            </div>
            {/* <Link legacyBehavior href="/shopping-cart"> */}
            {/* <a className="btn btn-light border position-relative ms-2 fw-normal"> */}
            <div className="btn btn-light border position-relative ms-2 fw-normal">
              <FontAwesomeIcon icon={["fas", "shopping-cart"]} />
              &nbsp;Cart
              <span className="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger my-auto">
                3
              </span>
              {/* </a> */}
            </div>
            {/* </Link> */}
          </div>
        </div>
      </nav>
      {!simple && (
        <nav className="navbar navbar-expand-lg navbar-light bg-white border-bottom">
          <div className="container">
            <button
              className="navbar-toggler ms-auto"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navbarNavDropdown"
              aria-controls="navbarNavDropdown"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbarNavDropdown">
              <ul className="navbar-nav">
                {
                  categories.map((category) => {
                    return (<li className="nav-item">
                      <Link legacyBehavior href={`/explore?cat=${category}`}>
                        <a className="nav-link">{category}</a>
                      </Link>
                    </li>);
                  })
                }
              </ul>
              <ul className="ms-auto navbar-nav">
                <li className="nav-item dropdown">
                  <a
                    href="#"
                    className="nav-link dropdown-toggle"
                    role="button"
                    data-bs-toggle="dropdown"
                    aria-expanded="false"
                    id="languageMenuLink"
                  >
                    English
                  </a>
                  <ul
                    className="dropdown-menu dropdown-menu-macos dropdown-menu-end"
                    aria-labelledby="languageMenuLink"
                  >
                    <li>
                      <a href="#" className="dropdown-item">
                        English
                      </a>
                    </li>
                    <li>
                      <a href="#" className="dropdown-item mt-1">
                        日本語
                      </a>
                    </li>
                  </ul>
                </li>
              </ul>
            </div>
          </div>
        </nav>
      )}
    </header>
  );
}

export default Header;
