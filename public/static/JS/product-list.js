const limit = 5;
let offset = 0;

const NO_IMAGE = "/static/Resources/no-image.svg";

// Tunisianet -> Mytek -> Scoop -> placeholder, one hop per load error
function attachImageFallback(img, product) {
  const chain = [product["mytek"]?.["image"], product["scoopgaming"]?.["image"], NO_IMAGE].filter(Boolean);
  img.addEventListener("error", () => {
    const next = chain.shift();
    if (next) img.src = next;
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const productList = document.getElementById("product-list");
  const Sentinel = document.getElementById("sentinel");

  function best_price_(product) {
    min = product["tunisianet"]?.["price"];
    if (product["mytek"] && product["mytek"]["price"] < min) {
      min = product["mytek"]["price"];
    }
    if (product["scoopgaming"] && product["scoopgaming"]["price"] < min) {
      min = product["scoopgaming"]["price"];
    }
    return min;
  }

  function createProductCard(product) {
    const card = document.createElement("li");
    card.className = "product-card";
    console.log("Tunisianet Price: ", product["tunisianet"]?.["price"]);
    console.log("Mytek Price: ", product["mytek"]?.["price"]);
    console.log(
      "ScoopGaming Price: ",
      product["scoopgaming"]?.["price"]
        ? product["scoopgaming"]?.["price"]
        : "Unavailable"
    );
    best_price = best_price_(product);
    console.log("Best Price: ", best_price);
    console.log(best_price == product["tunisianet"]?.["price"]);
    console.log(best_price == product["mytek"]?.["price"]);
    console.log(best_price == product["scoopgaming"]?.["price"]);

    if (product["mytek"]) {
      mytek = `
          <a href="${product["mytek"]["link"]}" target="_blank" rel="noopener noreferrer" class="product-link ${
        best_price === product["mytek"]["price"] ? "best-price" : ""
      }">
              <img src="${MytekLogo}" alt="Mytek Logo" class="price-logo-img">
              <span class="price" id="mytek-price">${
                product["mytek"]["price"]
              }</span>
          </a>
      `;
    } else {
      mytek = `
          <div class="product-link ${
            best_price === product["mytek"]?.["price"] ? "best-price" : ""
          }">
              <img src="${MytekLogo}" alt="Mytek Logo" class="price-logo-img">
          </div>
      `;
    }
    if (product["scoopgaming"]) {
      scoopgaming = `
          <a href="${product["scoopgaming"]["link"]}" target="_blank" rel="noopener noreferrer" class="product-link ${
        best_price === product["scoopgaming"]["price"] ? "best-price" : ""
      }">
              <img src="${ScoopGamingLogo}" alt="ScoopGaming Logo" class="price-logo-img">
              <span class="price" id="scoopgaming-price">${
                product["scoopgaming"]["price"]
              }</span>
          </a>
      `;
    } else {
      scoopgaming = `
          <div class="product-link">
              <img src="${ScoopGamingLogo}" alt="ScoopGaming Logo" class="price-logo-img">
          </div>
      `;
    }
    card.innerHTML = `
        <div class="product-card-div">
            <div class="product-img-div">
                <img src="${product["tunisianet"]["image"]}" alt="${product["tunisianet"]["title"]}" class="product-img">
            </div>
            <div class="product-title-div">
                <h3 class="product-title">${product["tunisianet"]["title"]}</h3>
            </div>
            <div class="price-list-div">
                <div class="price-item">
                    <a href="${
                      product["tunisianet"]["link"]
                    }" target="_blank" rel="noopener noreferrer" class="product-link ${
      best_price === product["tunisianet"]["price"] ? "best-price" : ""
    }">
                        <img src="${TunisianetLogo}" alt="Tunisianet Logo" class="price-logo-img">
                        <span class="price" id="tunisianet-price">${
                          product["tunisianet"]["price"]
                        }</span>
                    </a>
                </div>
                <div class="price-item">
                    ${mytek}
                </div>
                <div class="price-item">
                    ${scoopgaming}
                </div>
            </div>    
        </div>
    `;
    attachImageFallback(card.querySelector(".product-img"), product);
    return card;
  }

  let loading = false;
  let queued = false; // a sentinel hit arrived while a load was running
  let retried = false; // one retry per run of failures, never a loop

  function sentinelInView() {
    if (!Sentinel) return false;
    return Sentinel.getBoundingClientRect().top <= window.innerHeight + quarterScreenHeight;
  }

  // The observer only fires when the sentinel crosses into view. After a failed or
  // dropped load nothing would fire again, so look at the sentinel once more.
  function recheckLater() {
    setTimeout(() => {
      if (sentinelInView()) loadProducts();
    }, 1000);
  }

  async function loadProducts() {
    if (loading) {
      queued = true;
      return;
    }
    loading = true;
    let ok = false;
    try {
      const response = await fetch(
        `/load_products?limit=${limit}&offset=${offset}&product_type=${product_type}`
      );
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      const products = await response.json();
      ok = true;
      if (products.length === 0) {
        observer.disconnect();
        queued = false;
        return;
      }
      products.forEach((product) => {
        console.log(product);
        const productCard = createProductCard(product);
        console.log(product["Title"]);
        // Assuming each item has a 'product_name' property
        productList.appendChild(productCard);
      });

      offset += limit;
    } catch (error) {
      console.error("Error loading products:", error);
    } finally {
      loading = false;
    }
    if (ok) {
      retried = false;
      if (queued) {
        queued = false;
        recheckLater();
      }
    } else if (!retried) {
      retried = true;
      recheckLater();
    }
  }

  const quarterScreenHeight = window.innerHeight / 4;
  const observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) {
        console.log("Loading more products...");
        loadProducts();
      }
    },
    {
      rootMargin: `0px 0px ${quarterScreenHeight}px 0px`,
    }
  );

  if (Sentinel) {
    observer.observe(Sentinel);
  } else {
    console.error("Sentinel element not found in the DOM.");
  }
});
