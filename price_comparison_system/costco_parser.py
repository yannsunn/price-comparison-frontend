
import json
import re

def parse_costco_markdown(markdown_content):
    products = []
    product_pattern = re.compile(
        r'\!\[(?P<img_alt>[^\]]+)\]\((?P<img_url>[^\)]+)\)\s*\n+'  # 画像とALTテキスト
        r'(?:¥(?P<price>[0-9,]+)\s*\n+)?'  # 価格 (オプション)
        r'(?:.*?\n)*?' # 価格と商品名リンクの間の任意の行 (非貪欲、複数行対応)
        r'\[(?P<product_name>[^\]]+)\]\((?P<product_url>[^\)]+)\)' # 商品名とURL
        , re.DOTALL
    )

    for match in product_pattern.finditer(markdown_content):
        product_name = match.group('product_name').strip()
        price_str = match.group('price')
        price = int(price_str.replace(',', '')) if price_str else None
        product_url = match.group('product_url').strip()

        if product_name and product_url:
            products.append({
                'product_name': product_name,
                'price': price,
                'url': product_url
            })
    return products

