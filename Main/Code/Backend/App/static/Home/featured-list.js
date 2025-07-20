const list = ["Lenovo Loq", "MSI GF63", "Dell G15", "HP Pavilion Gaming", "Acer Nitro 5", "Asus TUF Gaming", "Razer Blade 15", "Gigabyte Aorus 15G", "Alienware m15 R6", "Apple MacBook Pro 16"];

const featuredList = document.getElementById("featured-list");

// list.forEach((item) => {
//     const listItem = document.createElement("li");
//     listItem.textContent = item;
//     featuredList.appendChild(listItem);
// });

fetch("../Resources/JSON/laptops.json")
.then(response => {
    if (!response.ok) {
        throw new Error("Network response was not ok");
    }
    return response.json();
})
.then(data => {
    data.forEach((item) => {
        const productCard = createProductCard(item);
        console.log(item["Title"]);
        // Assuming each item has a 'product_name' property
        featuredList.appendChild(productCard);
    });
}).catch(error => {
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
