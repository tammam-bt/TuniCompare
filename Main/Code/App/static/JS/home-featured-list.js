const featuredList = document.getElementById("featured-list");
const limit = 5;
let offset = Math.floor(Math.random() * 10) + 1; // Random offset for featured products
const product_types = ["pc_portable_gamer", "pc_bureau_gamer", "ecran_gamer"];
const product_type =
  product_types[Math.floor(Math.random() * product_types.length)];

async function fetchFeaturedProducts() {
  const response = await fetch(
    `/load_products?limit=${limit}&offset=${offset}&product_type=${product_type}`
  );

  if (!response.ok) {
    throw new Error("Network response was not ok");
  }

  const data = await response.json();
  data.forEach((item) => {
    const productCard = createProductCard(item);
    console.log(item["Title"]);
    // Assuming each item has a 'product_name' property
    featuredList.appendChild(productCard);
  });
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
          <a href="${product["mytek"]["link"]}" class="product-link ${
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
          <div class="product-link no-info">
              <img src="${MytekLogo}" alt="Mytek Logo" class="price-logo-img">
          </div>
      `;
  }
  if (product["scoopgaming"]) {
    scoopgaming = `
          <a href="${product["scoopgaming"]["link"]}" class="product-link ${
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
          <div class="product-link no-info">
              <img src="${ScoopGamingLogo}" alt="ScoopGaming Logo" class="price-logo-img">
          </div>
      `;
  }
  card.innerHTML = `
        <div class="product-card-div">
            <div class="product-img-div">
                <img src="${product["tunisianet"]["image"]}" alt="${
    product["tunisianet"]["title"]
  }" class="product-img">
            </div>
            <div class="product-title-div">
                <h3 class="product-title">${product["tunisianet"]["title"]}</h3>
            </div>
            <div class="price-list-div">
                <div class="price-item">
                    <a href="${
                      product["tunisianet"]["link"]
                    }" class="product-link ${
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
  return card;
}

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

document.addEventListener("DOMContentLoaded", () => {
  fetchFeaturedProducts().catch((error) => {
    console.error("Error fetching featured products:", error);
  });
});
