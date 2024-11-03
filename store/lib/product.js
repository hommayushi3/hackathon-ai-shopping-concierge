import { parse } from 'csv-parse/sync';

const DATA_PATH = "/data";
let db = new Map();

export async function getDb() {
    if (db.size === 0) {
        console.log("reading db");
        const filePath = `${DATA_PATH}/product_catalog_v2.csv`;
        const resp = await fetch(filePath);
        const csv = await resp.text();
        const records = parse(csv, { columns: true });
        console.log(`Loaded ${records.length} records`)
        for (const record of records) {
            db[record.article_id] = record;
        }
    }
    return db;
}

export async function getProductData(productId) {
    const db = await getDb();
    const data = db[productId];
    if (!data) {
        console.error(`${productId} not found`);
        return {};
    }
    return data;
}

export function getProductInfo(product) {
    // default values
    let id = "0";
    let productName = "";
    let category = "";
    let price = "";
    let priceNum = 0;
    let description = "";
    let color = "";
    // Load real values
    if (product && Object.keys(product).length) {
        id = product['article_id'];
        productName = product['prod_name'];
        category = product['index_group_name'];
        price = formatPrice(product['price']);
        priceNum = Number(product['price']);
        description = product['detail_desc'];
        color = product['colour_group_name'];
    }
    return {
        id: id,
        productName: productName,
        category: category,
        price: price,
        description: description,
        color: color,
        priceNum: priceNum
    }
}

export async function getProductName(productId) {
    return await getProductData(productId)["prod_name"];
}

export function getProductImage(productId) {
    return `${DATA_PATH}/product_catalog_images/0${productId}.jpg`;
}

export function formatPrice(priceStr) {
    return `$${Number(priceStr).toFixed(2)}`;
}

export function getProductLink(id) {
    return `/product/${id}`;
}

export function getCheckoutLink(id) {
    return `/checkout/confirm-checkout?article_ids=${id}`;
}
