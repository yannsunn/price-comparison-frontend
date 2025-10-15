() => {
    const products = [];
    document.querySelectorAll("li.product-list__item").forEach(item => {
        const nameElement = item.querySelector("a.product-card__name");
        const priceElement = item.querySelector("span.price");
        if (nameElement && priceElement) {
            const productName = nameElement.innerText.trim();
            const productUrl = nameElement.href;
            const priceText = priceElement.innerText.trim().replace(/[^0-9]/g, ''); // 数字のみ抽出
            const price = parseInt(priceText, 10);
            products.push({
                product_name: productName,
                price: price,
                url: productUrl
            });
        }
    });
    return products;
}
