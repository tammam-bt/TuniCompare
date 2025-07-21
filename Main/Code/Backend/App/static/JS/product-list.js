const list = [
  "Lenovo Loq",
  "MSI GF63",
  "Dell G15",
  "HP Pavilion Gaming",
  "Acer Nitro 5",
  "Asus TUF Gaming",
  "Razer Blade 15",
  "Gigabyte Aorus 15G",
  "Alienware m15 R6",
  "Apple MacBook Pro 16",
];

const productList = document.getElementById("product-list");

// list.forEach((item) => {
//     const listItem = document.createElement("li");
//     listItem.textContent = item;
//     featuredList.appendChild(listItem);
// });

fetch(productListJsonUrl)
  .then((response) => {
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return response.json();
  })
  .then((data) => {
    data.forEach((item) => {
      const productCard = createProductCard(item);
      console.log(item["Title"]);
      // Assuming each item has a 'product_name' property
      productList.appendChild(productCard);
    });
  })
  .catch((error) => {
    console.error("Error fetching data:", error);
  });

function createProductCard(product) {
  const card = document.createElement("li");
  card.className = "product-card";
  card.innerHTML = `
        <div class="product-card-div">
            <div class="product-img-div">
                <img src="${product["Image"]}" alt="${product["Title"]}" class="product-img">
            </div>
            <div class="product-title-div">
                <h3 class="product-title">${product["Title"]}</h3>
            </div>
            <div class="price-list-div">
                <div class="price-item">
                    <a href="${product["Link"]}" class="product-link best-price">
                        <img src="${MytekLogo}" alt="Mytek Logo" class="price-logo-img">
                        <span class="price" id="mytek-price">${product["Price"]}</span>
                    </a>
                </div>
                <div class="price-item">
                    <a href="${product["Link"]}" class="product-link">
                        <img src="${TunisianetLogo}" alt="Tunisianet Logo" class="price-logo-img">
                        <span class="price" id="tunisianet-price">${product["Price"]}</span>
                    </a>
                </div>
                <div class="price-item">
                    <a href="${product["Link"]}" class="product-link">
                        <img src="${ScoopGamingLogo}" alt="ScoopGaming Logo" class="price-logo-img">
                        <span class="price" id="scoopgaming-price">${product["Price"]}</span>
                    </a>
                </div>
            </div>    
        </div>
    `;
  return card;
}
