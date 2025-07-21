const featuredList = document.getElementById("featured-list");

fetch(laptopsJsonUrl)
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
      featuredList.appendChild(productCard);
    });
  })
  .catch((error) => {
    console.error("Error fetching data:", error);
  });

function createProductCard(product) {
  const card = document.createElement("li");
  card.className = "product-card";
  card.innerHTML = `
        <a href="${product["Link"]}" class="product-link">
        <div class="product-img">
        <img src="${product["Image"]}" alt="${product["Title"]}">
        </div>
        <h3 class="product-title">${product["Title"]}</h3>
        <span class="price">${product["Price"]}</span>
        </a>
    `;
  return card;
}
